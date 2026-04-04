# 😊 Classificador de Emoções com Rede Neural

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-%235C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)

> Uma aplicação fullstack que utiliza **Inteligência Artificial com Rede Neural** para identificar emoções em fotos de forma automática.

---

## ✨ Funcionalidades

- **Classificação de Emoções:** Detecta emoções a partir de imagens inseridas pelo usuário.
- **Interface Web Intuitiva:** Frontend moderno para envio de imagens e visualização dos resultados.
- **Backend em Python:** API para processamento e inferência do modelo de IA.
- **Modelo Intuitivo:** Construído em PyTorch com auxílio do OpenCV para indentificação de rostos
- **Treinamento e Experimentos:** Suporte a notebooks para análise e evolução do modelo.
- **Dockerizado:** Ambiente pronto para execução com Docker Compose.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Desktop instalados.

### Executando a Aplicação

Na raiz do projeto, rode:

```bash
docker-compose up --build
```

---

## 🔗 Acesso à Aplicação

Após os containers iniciarem com sucesso, acesse:

### 🏠 Localhost (Rodando na sua máquina)

| Serviço | URL | Descrição |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:8080` | Interface Visual (React + TypeScript) |
| **Backend** | `http://localhost:5000` | API de Classificação (Python) |

---

## 🧠 Tecnologias Utilizadas

- **Frontend:** React.js + TypeScript
- **Backend:** Flask + Python
- **IA / Dados:** Jupyter Notebook + PyTorch(treinamento e testes de modelo)
- **Infraestrutura:** Docker / Docker Compose

---

## 📁 Estrutura Geral do Projeto

```bash
Emotions-RedeNeural/
├── frontend/              # Interface da aplicação
├── backend/               # API e lógica de classificação
├── docker-compose.yml
└── README.md
```
