from flask import Flask,jsonify,request
from flask_cors import CORS
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
import torch.nn as nn
import pandas as pd
import numpy as np
from scipy.stats import zscore
import mne  

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

def processar_csv_em_memoria(arquivo_csv):
    canais_oficiais = ['AF3', 'AF4', 'F3', 'F4', 'F7', 'F8', 'FC5', 'FC6', 'O1', 'O2', 'P7', 'P8', 'T7', 'T8']
    
    df = pd.read_csv(arquivo_csv)
    if all(canal in df.columns for canal in canais_oficiais):
        df_limpo = df[canais_oficiais]
    else:
        df_limpo = df.iloc[:, :14]
        
    df_volts = df_limpo.T * 1e-6
    array_volts = df_volts.to_numpy()
    
    info = mne.create_info(ch_names=canais_oficiais, sfreq=128, ch_types='eeg')
    info.set_montage('standard_1020')
    raw = mne.io.RawArray(array_volts, info, verbose=False)
    
    raw.filter(l_freq=0.5, h_freq=45.0, fir_design='firwin', verbose=False)
    
    epochs = mne.make_fixed_length_epochs(raw, duration=1.0, overlap=0.5, verbose=False)
    matriz_3d = epochs.get_data() # Formato: (Lotes, 14, 128)
    
    matriz_3d_norm = zscore(matriz_3d, axis=2)
    matriz_3d_norm = np.nan_to_num(matriz_3d_norm)
    
    return matriz_3d_norm

@app.route('/chute',methods=['POST'])
def previsao():
    if 'file' not in request.files:
        return jsonify({'erro': 'Arquivo não encontrado'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'erro' : 'Nenhum arquivo selecionado'}), 400
    
    try:
        array3d = processar_csv_em_memoria(file)
        tensor_entrada = torch.tensor(array3d,dtype=torch.float32).to(device)

        with torch.no_grad():
            outputs = modeloProducao(tensor_entrada)
            probabilidades = torch.nn.functional.softmax(outputs,dim=1)
            probabilidade_media = torch.mean(probabilidades, dim=0)
            confianca, chutado = torch.max(probabilidade_media,1)
            jogo = dicionario_jogos[chutado.item()]

        return jsonify({
            'jogo':jogo,
            'probabilidade': round(confianca.item() * 100, 2),
            'janelas_analisadas': array3d.shape[0]
        })

    except Exception as e:
        return jsonify({'erro':str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000,host='0.0.0.0',debug=True)