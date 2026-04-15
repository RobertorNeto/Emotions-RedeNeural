# 🧠😊 Classificador de Emoções (EEG) com CNN 1D

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter%20Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

> Projeto focado em **Machine Learning** para **classificar jogo/emoção** a partir de **sinais de EEG**, utilizando uma **CNN 1D** (redes neurais convolucionais 1D) e um pipeline reproduzível para treino, validação e testes.

---

## ✨ Funcionalidades

- **Classificação de Emoções/Jogo via EEG:** Prediz a classe alvo a partir de sinais temporais (EEG).
- **Modelo com CNN 1D:** Arquitetura voltada para séries temporais e sinais biomédicos.
- **Pipeline de Treinamento e Avaliação:** Rotina de treino/validação/teste com métricas.
- **Experimentos e Análises:** Suporte a notebooks para exploração, visualização e iteração rápida.
- **Dockerizado:** Ambiente pronto para execução com Docker Compose.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Desktop instalados.

### Executando o Ambiente

Na pasta do projeto, rode:

```bash
docker-compose up --build
```

> Se o container expuser portas (ex.: Jupyter), consulte o `docker-compose.yml` para ver o mapeamento correto.

---

## 🔗 Acesso (quando aplicável)

Dependendo do `docker-compose.yml`, você pode ter serviços como:

- **Jupyter Notebook/Lab** (para experimentos e análises)
- **Serviço de Treinamento** (execução de treino/avaliação via container)

> Os endpoints/portas variam conforme a configuração do Compose. Verifique o arquivo `docker-compose.yml`.

---

## 🧠 Tecnologias Utilizadas

- **Linguagem:** Python
- **Deep Learning:** PyTorch
- **Experimentação:** Jupyter Notebook
- **Infraestrutura:** Docker / Docker Compose

---

## 📁 Estrutura Geral do Projeto

> Ajuste os comentários conforme os nomes reais das pastas/arquivos dentro do seu desafio.

```bash
Desafio-ML-ENGINEER/
├── aplicacao/            # Pasta com codigos e Notebooks
├── docker-compose.yml    # Orquestração do ambiente
└── README.md             # Documentação do projeto
```

---

## 📌 Observações

- Este projeto é orientado a **experimentos**: a evolução do modelo normalmente acontece via notebooks + ajustes no pipeline/modelo.
- Caso o dataset não esteja versionado no repositório, inclua-o conforme a estratégia do projeto (download, volume, ou instruções no Compose).

## Experimento de Ablação

Para justificar a complexidade do pipeline de pré-processamento e engenharia de features, conduzi um experimento de ablação avaliando o impacto da remoção de componentes-chave do sistema. As métricas abaixo refletem a Acurácia Média obtida através de validação estrita *GroupKFold* (Cross-Subject).

| Configuração do Pipeline | Baseline (Random Forest) | Deep Learning (CNN 1D) | Observação Técnica / Impacto |
| :--- | :--- | :--- | :--- |
| **Pipeline Completo** *(Filtro 0.5-45Hz + Z-Score + Features Estendidas)* | **71.54%** | **81.46%** | A convergência foi estável e a Matriz de Confusão apresentou forte diagonal principal. O RF se beneficiou enormemente das features extras de mínimo, máximo e frequência (70 features no total). |
| **Sem Filtro de Ruído** *(Sem MNE Bandpass, mantendo Z-score)* | 52.91% | 80.66% | A CNN é robusta e conseguiu extrair os padrões locais compensando parte do ruído, mas o Baseline estatístico despencou 18%, mostrando que a sujeira de 60Hz da rede elétrica destrói a média/desvio do sinal. |
| **Sem Normalização** *(Sinal Bruto, Sem Z-Score)* | 32.33% | 25.00% | **Colapso total do modelo.** Com 4 classes, 25% equivale a um chute aleatório (*Random Guessing*). A discrepância de amplitude entre os canais impediu a convergência dos gradientes na CNN. |
