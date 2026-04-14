
import streamlit as st
import requests
import time
import os
# ==========================================
# CONTROLE DE ESTADO (MEMÓRIA DO STREAMLIT)
# ==========================================
# Lembra se a análise já foi feita para travar a tela
if "analise_concluida" not in st.session_state:
    st.session_state.analise_concluida = False
# Guarda os resultados da IA para não sumirem da tela
if "dados_resultado" not in st.session_state:
    st.session_state.dados_resultado = None

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Synapsee - Análise de EEG",
    page_icon="🧠",
    layout="centered"
)

URL_BACKEND = os.getenv("BACKEND_URL", "http://localhost:5000/chute")

mapa_emojis = {
    "G1 - Calmo": "🧘‍♂️",
    "G2 - Neutro": "😐",
    "G3 - Terror ": "😱",
    "G3 - Terror": "😱", 
    "G4 - Chato": "🥱"
}

st.title("🧠 Synapsee: Deep Learning e EEG")
st.markdown("Faça o upload dos sinais captados para realizar a predição da emoção em tempo real utilizando uma arquitetura de CNN-1D.")

st.divider()

# ==========================================
# ÁREA DE UPLOAD (TRAVADA CONDICIONALMENTE)
# ==========================================
# O parâmetro 'disabled' lê a memória do Streamlit
arquivo_eeg = st.file_uploader(
    "Envie o arquivo de registro do paciente (.csv)", 
    type=["csv"],
    disabled=st.session_state.analise_concluida
)

# Botão de Reset (só aparece quando a análise já acabou)
if st.session_state.analise_concluida:
    if st.button("🔄 Realizar Nova Análise", use_container_width=True):
        # Limpa a memória e recarrega a tela
        st.session_state.analise_concluida = False
        st.session_state.dados_resultado = None
        st.rerun()

# Fluxo de execução quando há um arquivo e o sistema não está travado
if arquivo_eeg is not None and not st.session_state.analise_concluida:
    st.info(f"Arquivo carregado: `{arquivo_eeg.name}`. Pronto para inferência.")
    
    if st.button("Executar Rede Neural", type="primary", use_container_width=True):
        
        with st.spinner('Filtrando frequências e executando a predição na Rede Neural...'):
            try:
                conteudo_arquivo = arquivo_eeg.getvalue()
                payload = {"file": (arquivo_eeg.name, conteudo_arquivo)}
                
                inicio_tempo = time.time()
                resposta = requests.post(URL_BACKEND, files=payload)
                fim_tempo = time.time()
                
                if resposta.status_code == 200:
                    # Salva os resultados no st.session_state
                    st.session_state.dados_resultado = resposta.json()
                    st.session_state.dados_resultado['tempo'] = round(fim_tempo - inicio_tempo, 2)
                    
                    # Trava o sistema e recarrega a tela para aplicar o bloqueio
                    st.session_state.analise_concluida = True
                    st.rerun() 
                    
                else:
                    st.error(f"⚠️ O servidor retornou um erro (Código {resposta.status_code})")
                    st.json(resposta.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Falha de Conexão: O Backend não está respondendo. Verifique se o seu servidor Flask (app.py) ou Docker está ligado na porta 5000.")
            except Exception as e:
                st.error(f"🚨 Ocorreu um erro inesperado no Frontend: {str(e)}")

# ==========================================
# EXIBIÇÃO DOS RESULTADOS (DASHBOARD)
# ==========================================
# Exibe apenas se a IA já calculou e salvou os dados na memória
if st.session_state.analise_concluida and st.session_state.dados_resultado is not None:
    dados = st.session_state.dados_resultado
    
    jogo = dados.get("jogo", "Desconhecido")
    confianca = dados.get("probabilidade", 0.0)
    janelas = dados.get("janelas_analisadas", 0)
    tempo_processamento = dados.get("tempo", 0.0)
    
    st.success("✅ Processamento concluído com sucesso!")
    st.markdown("### 📊 Resultado da Avaliação")
    
    col1, col2, col3 = st.columns(3)
    emoji = mapa_emojis.get(jogo, "🧠")
    
    col1.metric("Emoção Dominante", f"{emoji} {jogo.split('-')[1].strip() if '-' in jogo else jogo}")
    col2.metric("Confiança da IA", f"{confianca}%")
    col3.metric("Janelas Analisadas", janelas)
    
    st.progress(int(confianca) / 100)
    st.caption(f"Tempo de inferência (Backend): {tempo_processamento} segundos")

st.divider()
st.caption("Desenvolvido para pipeline de Machine Learning Operations (MLOps).")