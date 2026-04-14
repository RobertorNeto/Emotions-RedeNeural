# 😊 Emotions-RedeNeural — Projetos de Classificação e Inferência de Emoções

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-%235C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

> Este repositório reúne **dois projetos** relacionados à **classificação e inferência de emoções** usando Inteligência Artificial:
>
> 1) **CNN 1D para classificar jogo/emoção a partir de sinais de EEG** (experimentos)  
> 2) **Plataforma fullstack para inferência de emoções em imagens (faces)**

---

## 📌 Projetos

### 1️⃣ Desafio-ML-ENGINEER — Classificador EEG (CNN 1D)

**Objetivo:** criar e avaliar uma **CNN 1D** para **classificar o jogo/emoção** com base em **dados de EEG** obtidos em experimentos.

**O que você encontra aqui:**
- Pipeline de treino e avaliação para séries temporais (EEG)
- Experimentos e notebooks (análises, validações, testes)
- Modelos em **PyTorch** voltados para **CNN 1D**

---

### 2️⃣ Desafio-AI-ENGINEER — Plataforma de Inferência de Emoções (Imagens)

**Objetivo:** aplicação **fullstack** que utiliza **Rede Neural** para identificar emoções em fotos automaticamente.

**Principais características:**
- **Frontend:** React + TypeScript
- **Backend:** Python (API para inferência)
- **Modelo:** PyTorch com apoio do OpenCV (ex.: detecção/recorte facial)
- **Dockerizado:** execução com Docker Compose

---

## ✨ Funcionalidades (Resumo)

- **Classificação em EEG (CNN 1D):** previsão de jogo/emoção a partir de sinais temporais.
- **Inferência em Imagens:** detecção e classificação de emoções a partir de fotos.
- **Execução simplificada:** ambos projetos sobem via **Docker Compose**.

---

## 🚀 Como Rodar os Projetos

### ✅ Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Desktop instalados.

---

## 🧠 Rodando o Projeto 1 (EEG — CNN 1D)

Entre na pasta do projeto e suba os serviços:

```bash
cd Desafio-ML-ENGINEER
docker-compose up --build
```

> Se o projeto expuser portas/serviços, consulte o `docker-compose.yml` dentro da pasta para ver os endpoints.

---

## 🖼️ Rodando o Projeto 2 (Inferência por Imagem — Fullstack)

Entre na pasta do projeto e suba os serviços:

```bash
cd Desafio-AI-ENGINEER
docker-compose up --build
```

> Após subir, consulte os endpoints/portas no `docker-compose.yml` do projeto (ex.: frontend/backend).

---

## 🧠 Tecnologias Utilizadas

- **Frontend:** React.js + TypeScript
- **Backend:** Python (ex.: Flask/FastAPI, conforme o projeto)
- **IA / Modelos:** PyTorch
- **Visão Computacional:** OpenCV
- **Experimentação:** Jupyter Notebook
- **Infraestrutura:** Docker / Docker Compose

---

## 📁 Estrutura do Repositório

```bash
Emotions-RedeNeural/
├── Desafio-AI-ENGINEER/      # Projeto 2: Plataforma fullstack (inferência em imagens)
│   ├── docker-compose.yml
│   └── ...
├── Desafio-ML-ENGINEER/      # Projeto 1: CNN 1D para EEG (classificação jogo/emoção)
│   ├── docker-compose.yml
│   └── ...
└── README.md                 # README global (este arquivo)
```

---

## 📚 Documentação

- **Desafio-ML-ENGINEER:** detalhes de dataset, treino e avaliação estão na própria pasta do projeto.
- **Desafio-AI-ENGINEER:** documentação detalhada está no README já existente dentro do projeto.
