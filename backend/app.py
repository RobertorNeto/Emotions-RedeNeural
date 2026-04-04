from datetime import datetime
from zoneinfo import ZoneInfo
import os
import uuid
from flask import Flask,jsonify,request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import torch
import torch.nn as nn
from torchvision import models, transforms
from flask import Flask, request, jsonify
from PIL import Image
import io
import cv2 
import numpy as np 


app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PASTA_UPLOADS = os.path.join('static', 'uploads')
os.makedirs(PASTA_UPLOADS, exist_ok=True) 

PASTA_DADOS = os.path.join(BASE_DIR, 'data')
os.makedirs(PASTA_DADOS, exist_ok=True)

app.config['UPLOAD_FOLDER'] = PASTA_UPLOADS
caminho_db = os.path.join(PASTA_DADOS, 'banco_historico.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{caminho_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Predicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emocao = db.Column(db.String(50), nullable=False)
    certeza = db.Column(db.String(20), nullable=False)
    todas_probabilidades = db.Column(db.Text, nullable=False) 
    url_imagem = db.Column(db.String(200), nullable=False)
    data_hora = db.Column(db.DateTime,default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")))

    
emocoes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.efficientnet_b0()
num_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_features, 7)
model.load_state_dict(torch.load('modeloEmocoes.pth',map_location=device))
model = model.to(device)
model.eval()
print("Modelo pronto para uso!")

rosto_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

data_transforms = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.route('/predict',methods=['POST'])
def gerarResposta():
    if 'file' not in request.files:
        return jsonify({'erro' : 'Nenhum Arquivo Enviado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400
    
    try:
        imagem_byte = file.read()
        imagem_pil = Image.open(io.BytesIO(imagem_byte)).convert('RGB')

        nome_arquivo = f"{uuid.uuid4().hex}.jpg"
        caminho_salvamento = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        imagem_pil.save(caminho_salvamento)
        url_da_imagem = request.host_url + 'static/uploads/' + nome_arquivo

        imagem = np.array(imagem_pil)
        cinza = cv2.cvtColor(imagem,cv2.COLOR_RGB2GRAY)
        faces = rosto_cascade.detectMultiScale(cinza,scaleFactor=1.1,minNeighbors=5,minSize=(30,30))


        if len(faces) == 0:
            predicao_erro = Predicao(
                emocao = "Não Detectado",
                certeza = "100%",
                todas_probabilidades = '',
                url_imagem = url_da_imagem
            )
            db.session.add(predicao_erro)
            db.session.commit()
            return jsonify({'erro': 'Nenhum rosto humano detectado na imagem.'}), 400
        
        x, y, w, h = faces[0]

        margem_y = int(h * 0.15)
        margem_x = int(w * 0.15)
        y_inicio = max(0, y - margem_y)
        y_fim = min(imagem.shape[0], y + h + margem_y)
        x_inicio = max(0, x - margem_x)
        x_fim = min(imagem.shape[1], x + w + margem_x)
        rosto_recortado = imagem[y_inicio:y_fim, x_inicio:x_fim]

        imagem_final = Image.fromarray(rosto_recortado)

        imagem_transformada = data_transforms(imagem_final)

        #a imagem vem com 3 canais [2,224,224] e o modelo espera 4, ai transforma pra batch de 1 imagem
        imagem_transformada = imagem_transformada.unsqueeze(0).to(device) 
        
        with torch.no_grad():
            outputs = model(imagem_transformada)
            probabilidades = torch.nn.functional.softmax(outputs[0], dim=0)
            _, chutado = torch.max(outputs.data,1)
            emocao = emocoes[chutado.item()]

            todas_probabilidades = {}
            for i, classe in enumerate(emocoes):
                porcentagem = round(probabilidades[i].item() * 100, 2)
                todas_probabilidades[classe] = f"{porcentagem}%"

            nova_predicao = Predicao(
                emocao=emocao,
                certeza=todas_probabilidades[emocao],
                todas_probabilidades=str(todas_probabilidades),
                url_imagem=url_da_imagem
            )
            db.session.add(nova_predicao)
            db.session.commit()

            return jsonify({
                'emocao_principal': emocao,
                'certeza_principal': todas_probabilidades[emocao],
                'todas_probabilidades': todas_probabilidades,
                'status': 'sucesso',
                'rosto_detectado': True
            })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    
@app.route('/history',methods=['GET'])
def getHistorico():
    historico = Predicao.query.order_by(Predicao.data_hora.desc()).all()

    lista =[]
    for item in historico:
        lista.append({
            'id':item.id,
            'emocao':item.emocao,
            'certeza':item.certeza,
            'url_imagem':item.url_imagem,
            'data_hora': item.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
            'todas_probabilidades':item.todas_probabilidades
        })

    return jsonify({
        'total_registros': len(lista),
        'historico': lista
    }), 200

@app.route('/history', methods=['DELETE'])
def delete_historico():
    try:
        db.session.query(Predicao).delete()
        db.session.commit()

        pasta = app.config['UPLOAD_FOLDER']
        for arquivo in os.listdir(pasta):
            caminho_arquivo = os.path.join(pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)

        return jsonify({'message': 'Histórico deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar histórico'}), 500

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5000,host='0.0.0.0',debug=True)