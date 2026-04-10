# 🚀 Plano de Deploy AWS — Emotion-Rede Neural

Este documento descreve a estratégia de arquitetura e infraestrutura na nuvem AWS para colocar a plataforma de Reconhecimento de Emoções em produção, garantindo alta disponibilidade, segurança e escalabilidade.

---

## 1. Arquitetura de Serviços Proposta

Para a transição do ambiente local (Docker Compose) para a nuvem, a arquitetura será dividida para maximizar a performance e reduzir custos:

### Frontend (React/Vite)
- **Amazon S3** — Hospedagem dos arquivos estáticos compilados (`dist`).
- **Amazon CloudFront** — CDN global para entregar a interface estática com latência mínima aos usuários.

### Backend (API Flask + PyTorch)
- **Amazon ECS (Elastic Container Service) com AWS Fargate** — Como a API já está conteinerizada, o Fargate rodará os containers de forma serverless (sem necessidade de gerenciar instâncias EC2), facilitando a escala horizontal.
- **Application Load Balancer (ALB)** — Para distribuir o tráfego de entrada entre as múltiplas tarefas (containers) ativas do backend.

### Banco de Dados & Storage
- **Amazon RDS (PostgreSQL)** — Substituição do SQLite local. O RDS gerencia backups, redundância (Multi-AZ) e suporta alta concorrência de leitura/escrita para o histórico da sessão.
- **Amazon S3 (Bucket de Uploads)** — Substituição da pasta local `static/uploads`. As imagens enviadas pelos usuários serão salvas aqui, e o banco de dados armazenará apenas a URL pública (ou pré-assinada) do S3.

---

## 2. Fluxo de Dados

1. **Acesso** — O usuário acessa a aplicação via navegador. O CloudFront serve o frontend em milissegundos.
2. **Captura e Envio** — O usuário tira uma foto via webcam. O frontend empacota a imagem e envia um `POST /predict` para o Load Balancer (ALB).
3. **Processamento** — O ALB roteia a requisição para um container disponível no ECS (Fargate).
4. **Armazenamento de Mídia** — O container Flask faz o upload da foto original para o Amazon S3 e recebe a URL de volta.
5. **Inferência** — A imagem passa pelo pipeline do OpenCV (Haar Cascades com padding) e é convertida em um tensor. O modelo EfficientNet-B0 gera a predição via função Softmax.
6. **Persistência** — O backend grava a predição (emoção, métricas de confiança e a URL do S3) no Amazon RDS.
7. **Resposta** — O backend devolve o JSON completo para o frontend, que renderiza os dados dinamicamente na tela.

---

## 3. Estratégia de Escala

- **Auto Scaling do ECS** — O serviço Fargate será configurado com uma política de *Target Tracking Scaling*. Se a utilização média de CPU dos containers passar de 70% (devido a um pico de análises simultâneas), o ECS subirá novas réplicas do container Flask automaticamente.

- **CPU vs GPU** — O modelo EfficientNet-B0 é extremamente leve. Para este MVP, inferência em CPU (Fargate padrão) é suficiente e financeiramente eficiente. Caso no futuro migremos para um modelo mais pesado, a arquitetura permite transição para instâncias EC2 com GPUs.

- **Conexão com Banco** — Utilização do **RDS Proxy** para evitar esgotamento de conexões no PostgreSQL caso o número de containers Flask escale rapidamente.

---

## 4. Principais Riscos e Mitigações

| Risco Mapeado | Impacto | Estratégia de Mitigação |
|---|---|---|
| **Tamanho do Container (Cold Start)** | Bibliotecas como PyTorch e OpenCV são pesadas (imagens Docker > 1.5GB). Isso atrasa o tempo para subir novos containers em picos de acesso. | Usar a versão `pytorch-cpu` e `opencv-python-headless`. Manter sempre uma capacidade mínima de 2 containers rodando (`Desired Count = 2`) para garantir disponibilidade imediata. |
| **Gargalo de Inferência (Síncrono)** | O Flask é síncrono. Muitas requisições pesadas ao mesmo tempo podem bloquear o servidor e dar Timeout. | Configurar o **Gunicorn** (WSGI) com múltiplos workers dentro do container. Em uma arquitetura futura, migrar a inferência para uma fila assíncrona com FastAPI ou Django. |
| **Alto custo financeiro (Dinheiro)** | Manter infraestruturas na nuvem ocupando bastante memória e instâncias pode ser extremamente custoso principalmente para projetos de menor escala ou que não necessitem de tanta escalabilidade | Mudar a infraestrutura de nuvem para Railway + Vercel que possuem planos gratuitos generosos e não tão caros. |

---

## 5. Pipeline de CI/CD

Para garantir integrações contínuas, utilizaremos o **GitHub Actions**:

1. **Push na `main`** — Dispara os testes automatizados e atualização de Deploy.
2. **Build** — Cria a imagem Docker e envia para o **Amazon ECR** (Elastic Container Registry).
3. **Deploy** — Atualiza a Task Definition do ECS Fargate para subir os novos containers sem downtime (**Rolling Update**).


------------------------------------- || -------------------------------------
# 1. Arquitetura de Serviços Escolhida
 
Para garantir a máxima velocidade de entrega sem perder escalabilidade e menores custos de infraestrutura e facilidade para deploys menores, eu proponho uma infraestrutura diferente:
 
- **Frontend:** Vercel
- **Backend (API + IA):** Railway
- **Banco de Dados & Storage:** Railway PostgreSQL
 
---
 
## 2. Deploy do Frontend (Vercel)
 
A Vercel é o padrão para aplicações React/Vite devido à sua integração automática com github e projetos Node.js.
 
- **Integração:** O repositório do GitHub será conectado diretamente à Vercel.
- **Configuração de Build:**
  - Framework Preset: `Vite`
  - Build Command: `npm run build`
  - Output Directory: `dist`
- **Variáveis de Ambiente:** Será configurada a variável `VITE_API_URL` apontando para o domínio público gerado pelo Railway (ex: `https://synapsee-api-production.up.railway.app`), garantindo que o frontend saiba onde fazer o fetch das informações.
- **Vantagem:** Qualquer push na branch `main` gera um deploy automático com Zero Downtime e invalidação automática de cache global.
 
---
 
## 3. Deploy do Backend (Railway)
 
O Railway foi escolhido para hospedar a API Flask e o modelo PyTorch por sua facilidade de deploy via `Dockerfile` e provisionamento de banco de dados em um clique.
 
- **Estratégia de Container:** O Railway lerá o `Dockerfile`.
- **Ajuste Necessário de Porta:** Containers na nuvem não podem forçar a porta 5000. O código do Flask será ajustado para ler a variável de ambiente do sistema:
 
```python
import os
porta = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=porta)
```
 
- **Gerenciamento de Memória:** O PyTorch exige um consumo considerável de RAM. O serviço no Railway será configurado com pelo menos **1 GB a 2 GB de RAM** para evitar erros de Out of Memory (OOM) durante a inferência.
 
---
 
## 4. Banco de Dados e Armazenamento
 
Migrar de um ambiente local (Docker Compose) Railway exige duas mudanças fundamentais de arquitetura:
 
### A. Banco de Dados — Migração para PostgreSQL
 
O SQLite não é o padrão do Railway, por isso tem de mudar a arquitetura do banco para PostgreSQL
 
- **Solução:** Provisionar um serviço de PostgreSQL dentro do projeto no Railway.
- Apenas a `DATABASE_URL` no Flask será alterada para apontar para o banco em nuvem, mantendo o ORM (SQLAlchemy) intacto.
 
### B. Armazenamento das Imagens — Storage Externo
 
Pelo mesmo motivo acima, a pasta local `static/uploads` seria apagada a cada novo deploy no Railway.
 
- **Solução:** O backend Flask será integrado a um serviço de Storage Externo, como o **Cloudinary**.
- **Fluxo:** Ao receber a foto, o Flask faz o upload direto para o Cloudinary, recebe a URL pública segura e salva apenas essa URL no banco de dados PostgreSQL.
 
---
 
## 5. Fluxo de Integração Contínua (CI/CD)
 
A grande vantagem dessa stack é a automação completa sem necessidade de configurar GitHub Actions complexas e um deploy para uma infraestrutura menor e com custo reduzido:
 
1. O desenvolvedor faz um `git push` para a branch `main`.
2. A **Vercel** intercepta o código da pasta `/frontend`, compila e distribui globalmente.
3. O **Railway** intercepta a pasta `/backend`, faz o build da imagem Docker com o modelo PyTorch e sobe o novo container.
4. Em menos de **3 minutos**, a plataforma inteira está atualizada em produção.