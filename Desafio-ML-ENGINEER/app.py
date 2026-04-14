from flask import Flask,jsonify,request
from flask_cors import CORS
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
import torch.nn as nn
import pandas as pd
import numpy as np

class EmotionCNN(nn.Module):
    def __init__(self):
        super(EmotionCNN,self).__init__()

        self.conv1 = nn.Conv1d(in_channels=14,out_channels=32,kernel_size=5,padding=2)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool1d(kernel_size=2)

        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5, padding=2)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool1d(kernel_size=2)

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(in_features=64*32, out_features=128)
        self.relu3 = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(in_features=128, out_features=4)

    def forward(self,x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.flatten(x)
        x = self.dropout(self.relu3(self.fc1(x)))
        x = self.fc2(x)
        return x
    


dicionario_jogos = {
    0 : "G1 - Calmo",
    1 : "G2 - Neutro",
    2 : "G3 - Terror ",
    3 : "G4 - Chato"
}

app = Flask(__name__)
CORS(app)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
modeloProducao = EmotionCNN().to(device)
modeloProducao.load_state_dict(torch.load('cnn1d.pth',map_location=device))
modeloProducao.eval()
print("Modelo Pronto para Produção")

@app.route('/chute',methods=['POST'])
def previsao():
    if 'file' not in request.files:
        return jsonify({'erro': 'Arquivo não encontrado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'erro' : 'Nenhum arquivo selecionado'}), 400
    
    try:
        df = pd.read_csv(file)
        array2d = df.to_numpy()

        array3d = np.expand_dims(array2d,axis=0)
        tensor_entrada = torch.tensor(array3d,dtype=torch.float32).to(device)

        with torch.no_grad():
            outputs = modeloProducao(tensor_entrada)
            probabilidade = torch.nn.functional.softmax(outputs,dim=1)
            confianca, chutado = torch.max(probabilidade,1)
            jogo = dicionario_jogos[chutado.item()]

        return jsonify({
            'jogo':jogo,
            'probabilidade': confianca.item()*100
        })

    except Exception as e:
        return jsonify({'erro':str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000,host='0.0.0.0',debug=True)