# PLANO.md — Desafio Técnico AI Engineer (Synapsee)

## 1. Visão Geral e Arquitetura Proposta
A solução será desenvolvida com foco em modularidade, separando as responsabilidades de inferência (modelo), serviço (backend) e interface (frontend). 

**Decisões Preliminares:**
- **Modelo de IA:** Avaliação da família EfficientNet (foco no trade-off entre acurácia e tempo de inferência, comparando versões como B0 vs B1).
- **Biblioteca de ML:** Estruturação de Prós e Contras entre as arquiteturas utilizando PyTorch ou Tensorflow/keras.
- **Backend:** Python com Flask para expor a API REST, visando agilidade na prototipação e facilidade de integração com os tensores.
- **Frontend:** React.js para garantir uma interface de usuário interativa e uma experiência de uso fluida.
- **Infraestrutura:** Docker para conteinerização da aplicação, garantindo paridade entre o ambiente de desenvolvimento e de produção.

## 2. Cronograma e Etapas de Desenvolvimento
Abaixo estão as etapas planejadas para a execução do desafio, ordenadas logicamente e com o tempo estimado para cada fase. **Tempo total estimado:** ~22 horas.

| Fase | Tarefa | Tempo Estimado |
| :--- | :--- | :--- |
| **1. Planejamento** | Redação e estruturação deste documento (`PLANO.md`). | Concluído |
| **2. Pesquisa e Definição** | Estudo de arquiteturas (EfficientNet B0 vs B1), avaliação comparativa entre PyTorch e TensorFlow para o fluxo de treinamento, e pesquisa de datasets complementares ao FER-2013 para otimizar a eficiência. | 1h 30m |
| **3. Treinamento da IA** | Construção do script, fine-tuning do modelo a partir da arquitetura selecionada e exportação dos pesos finais. | 7h 00m |
| **4. Validação do Modelo** | Testes de inferência com imagens próprias, levantamento de métricas e plotagem da Matriz de Confusão para avaliar as taxas de acerto por emoção. | 1h 30m |
| **5. Construção do Backend** | Criação do servidor em Python (Flask) e desenvolvimento dos endpoints exigidos (`POST /predict` e `GET /history`). | 2h 00m |
| **6. Testes Iniciais de Rota**| Validação crua via Postman para garantir que o servidor sobe corretamente e responde às requisições HTTP básicas. | 0h 15m |
| **7. Integração Flask + Modelo**| Testes via Postman das rotas conectadas ao modelo treinado para validar o recebimento da imagem, inferência e retorno do nível de confiança. | 1h 00m |
| **8. Desenvolvimento do Frontend** | Construção da interface visual em React, focando na experiência do usuário para upload de imagens/acesso à câmera e histórico. | 4h 00m |
| **9. Integração Full-Stack** | Conexão do React com a API em Flask, garantindo fluxo de dados bidirecional e tratamento de estado. | 1h 00m |
| **10. Validação Ponta a Ponta** | Teste de funcionamento global, verificando se a captura visual, o envio, a predição e o display no histórico estão perfeitamente sincronizados. | 1h 00m |
| **11. Conteinerização** | Criação de Dockerfiles (Front e Back) para isolar o ambiente e facilitar a execução por terceiros. | 1h 30m |
| **12. Redação do Deploy.md** | Estruturação e escrita do plano detalhado de como essa solução seria colocada em produção na nuvem (AWS). | 1h 00m |

## 3. Estratégia de Testes e Integração
Para garantir que a integração **Back -> Modelo -> Front** funcione de forma robusta e sem gargalos, a validação ocorrerá em camadas:

1. **Isolamento via Postman:** Antes de envolver o React, garanto que o Flask consegue decodificar a imagem enviada via multipart/form-data ou base64, processá-la no formato exigido pelo modelo (ex: redimensionamento) e retornar um JSON formatado corretamente.
2. **Mocking no Frontend:** O desenvolvimento inicial do React ocorrerá recebendo dados estáticos em formato JSON para garantir que as barras de progresso (nível de confiança) e a tabela de histórico funcionem visualmente.
3. **Tratamento de Exceções:** A integração final testará ativamente os casos de falha (ex: envio de arquivos que não são imagens, perda de conexão com a API) para validar se o frontend reage de forma resiliente, apresentando mensagens claras de erro ao usuário em vez de quebrar a aplicação.