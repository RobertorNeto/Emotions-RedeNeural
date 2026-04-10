# PLANO.md — Desafio Técnico ML Engineer (Synapsee)

## 1. Decisões de Arquitetura e Justificativas

O objetivo deste projeto é construir um pipeline robusto para classificação de emoções a partir de sinais fisiológicos. Para garantir a viabilidade técnica e a entrega dentro do prazo estipulado, as seguintes decisões arquiteturais foram tomadas:

### Dataset
Adotarei o **GAMEEMO** (disponível via Kaggle) . Esta decisão dimnui o risco de bloqueio de cronograma devido à falta de acesso ao dataset do DEAP e garantindo um acesso mais fácil ao conjunto de dados.

### Pré-processamento e Limpeza
O tratamento dos dados brutos será feito com bibliotecas padrão de manipulação de dados do Pytohn (NumPy, Pandas) e, especificamente para os sinais de EEG, utilizarei a biblioteca **MNE-Python**. Os sinais passarão por filtragem (filtros passa-banda para isolar frequências de interesse cerebral, como as bandas Alpha e Beta) e serão segmentados em janelas temporais fixas (com *overlap* a definir empiricamente).

### Estratégia de Modelagem (Comparativa)
Para demonstrar um entendimento aprofundado sobre a extração de valor de sinais temporais e respeitar a necessidade de comparar abordagens, o pipeline ramificará o dado limpo para dois modelos:

1. **Modelo Baseline (Random Forest - Scikit-Learn):** Atuará como um marco de referência de acurácia. Como algoritmos baseados em árvores não processam bem séries temporais brutas, um módulo de *Feature Engineering* extrairá atributos estatísticos (média, variância) e de domínio da frequência de cada janela de sinal. É um modelo rápido, estável e interpretável.
2. **Modelo Avançado (CNN 1D - PyTorch):** Sinais fisiológicos são intrinsecamente sequenciais. Uma Rede Neural Convolucional 1D receberá as janelas temporais diretamente. A arquitetura será responsável por aprender a extração de *features* espaciais e temporais localmente. A escolha do PyTorch garante flexibilidade para iterar rapidamente sobre o design das camadas convolucionais.

### Plataforma de Inferência
O sistema será modularizado. O motor de inferência rodará em uma API utilizando **Flask** (Rápido e de fácil prototização), enquanto a interface com o usuário final será construída em **Streamlit**, permitindo o upload de arquivos de sinais brutos e a visualização simples das predições, sem adicionar complexidade desnecessária de front-end ao escopo.

---

## 2. Pipeline e Estimativa de Tempo

Considerando um prazo viável de **12 dias** para a entrega de ponta a ponta com rigor metodológico, o cronograma seguirá a seguinte estrutura:

* **Fase 1: Setup e Pré-processamento (Dias 1 - 2)**
    * Configuração de ambiente, repositório e gerenciador de dependências.
    * Download e Análise Exploratória (EDA) inicial do dataset GAMEEMO.
    * Desenvolvimento do script modular de limpeza, filtragem e segmentação de janelas (MNE-Python).
* **Fase 2: Feature Engineering e Baseline (Dias 3 - 5)**
    * Criação do extrator de *features* matemáticas (tempo/frequência) para as janelas.
    * Treinamento e avaliação inicial do modelo Random Forest.
* **Fase 3: Modelagem Avançada e Deep Learning (Dias 6 - 8)**
    * Construção da arquitetura CNN 1D no PyTorch.
    * Treinamento da rede neural consumindo os tensores de séries temporais limpas.
    * Ajuste de hiperparâmetros básicos.
* **Fase 4: Validação Rigorosa e Experimento de Ablação (Dias 9 - 10)**
    * Implementação do *Leave-One-Subject-Out* (LOSO) em ambos os modelos para avaliação *cross-sujeito* rigorosa.
    * Execução de ablação quantitativa (ex: re-treinar a CNN isolando a ausência do filtro de frequências) para documentar o valor de cada etapa do pipeline.
* **Fase 5: Produtização e Plataforma (Dias 11 - 12)**
    * Encapsulamento do modelo de melhor performance na API FastAPI.
    * Construção da interface no Streamlit para upload e visualização.
    * Polimento do repositório, documentação rigorosa no `README.md` com instruções de execução e preparação de argumentos técnicos para a defesa ao vivo.

---

## 3. Riscos Técnicos e Planos de Mitigação

**Risco 1: Curva de aprendizado no domínio de sinais fisiológicos**
Trabalhar com sinais crus como EEG exige cuidados específicos em relação a ruídos e calibração que fogem do processamento de dados comuns.
* *Mitigação:* Foco intensivo inicial na documentação do MNE-Python e literatura consolidada. A construção dos modelos será iniciada após construção das funções de limpeza de dados robustas.

**Risco 2: Overfitting (Memorização de Dados) e Viés de Sujeito**
Arquiteturas profundas, como a CNN 1D, treinadas em datasets biométricos com um baixo "N" de sujeitos únicos têm altíssima propensão ao overfitting. O modelo tende a "decorar" o ruído amostral ou os padrões biométricos únicos de um paciente (como uma linha de base cardíaca específica) em vez de aprender as features reais da emoção-alvo. Isso resulta em métricas ilusoriamente altas no conjunto de treino e falha crítica na capacidade de generalização para novos usuários.

* *Mitigação*: O controle desse risco será feito em duas frentes:

Validação: Isolamento estrito por sujeito. A separação dos dados ocorrerá pelo identificador do indivíduo (LOSO) antes de qualquer etapa de normalização global. Isso garante que o sujeito de teste seja uma instância puramente "zero-shot" para os pesos da rede, impedindo o vazamento de dados.

Arquitetura:  O modelo baseline (Random Forest) servirá como sanity check constante. Caso a CNN 1D apresente divergência drástica entre as métricas de treino e validação cruzada, aplicarei técnicas agressivas de regularização (Dropout, Weight Decay) e reduzirei a dimensionalidade das camadas convolucionais.