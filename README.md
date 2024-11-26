# Sistema de Identificação de Fases Semafóricas

## Descrição do Projeto

Este projeto apresenta o desenvolvimento de um sistema de visão computacional para identificação de fases semafóricas em imagens. Utilizando um pipeline de detecção e classificação, a aplicação é capaz de identificar e classificar semáforos usando algoritmos avançados de aprendizado de máquina. O sistema foi implementado em uma aplicação web interativa utilizando Flask.

**Resultados principais:**
- **YOLOv5**: Precisão de 94%, revocação de 97%, IoU médio de 98% para a detecção de semáforos.
- **MobileNetV3**: Acurácia de 99% e perda de 0.03 na classificação das fases semafóricas.

## Tecnologias Utilizadas

- **Linguagem**: Python 3.8.20
- **Framework Web**: Flask
- **Modelos de Machine Learning**:
  - YOLOv5 para detecção de semáforos.
  - MobileNetV3 para classificação das fases (verde, vermelho, amarelo).

## Requisitos

Certifique-se de que o Python 3.8.20 está instalado na sua máquina antes de continuar. Não há necessidade de hardware especializado como GPU ou CUDA para a execução deste projeto.

### Dependências

Todas as dependências estão listadas no arquivo `requirements.txt`. Para instalá-las, utilize o comando abaixo:

```bash
pip install -r requirements.txt
```

## Estrutura do Projeto

```plaintext
.
├── app.py                        # Arquivo principal que configura as rotas do sistema
├── functions.py                  # Funções auxiliares para o processamento
├── LICENSE                       # Arquivo de licença (MIT)
├── models/                       # Modelos treinados (detector e classifier)
│   ├── classifier/               # Modelos e dados para o classificador
│   │   ├── classes.txt           
│   │   ├── classifier.h5         
│   │   └── config.yaml           
│   └── detector/                 # Modelos e dados para o detector
│       ├── config.yaml           
│       ├── detector.pt           
├── README.md                     # Documentação do projeto
├── requirements.txt              # Dependências do projeto
├── static/                       # Arquivos estáticos utilizados no frontend
│   ├── classifier-result.png     
│   ├── detector-result.png       
│   ├── script.js                 
│   └── style.css                 
├── templates/                    # Arquivos de template para o frontend
│   └── index.html                
├── test/                          # Imagens para validação e testes
│   ├── test1.png                 
│   ├── test2.jpg                 
│   ├── test3.jpg                 
│   ├── test4.jpg                 
│   └── test5.jpg                 
```

## Executando o Projeto Localmente

### 1. Clonando o Repositório

Clone este repositório para a sua máquina local:

```bash
git clone https://github.com/DiasDavi/fase-semaforica.git
```

### 2. Instalando as Dependências

Navegue até a pasta do projeto e instale as dependências:


```bash
cd fase-semaforica
pip install -r requirements.txt
```

### 3. Executando o Projeto

Para iniciar a aplicação, execute o comando:

```bash
python app.py
```

A aplicação estará disponível em [http://localhost:5000](http://localhost:5000).

## Executando o Projeto com Docker

Se preferir executar o projeto utilizando Docker, siga as instruções abaixo:

### 1. Clonando o Repositório

Clone este repositório para a sua máquina local:

```bash
git clone https://github.com/DiasDavi/fase-semaforica.git
```

### 2. Criando a Imagem Docker

Navegue até a pasta do projeto:

```bash
cd fase-semaforica
```

Para construir a imagem Docker, use o comando:

```bash
docker build -t fase-semaforica:latest .
```

Este comando criará uma imagem Docker chamada `fase-semaforica` com a tag `latest`.

### 3. Executando o Container

Após criar a imagem, você pode executar o container usando:


```bash
docker build -t fase-semaforica:latest .
```

docker run -d -p 5000:5000 fase-semaforica:latest

Isso iniciará o container em segundo plano e a aplicação estará disponível em http://localhost:5000.

### 4. Verificando Logs do Container

Para verificar os logs do container em execução, use:

```bash
docker logs -f <container_id>
```

Substitua `<container_id>` pelo ID do container em execução, que você pode encontrar com o comando:

```bash
docker ps
```

### 5. Parando o Container

Para parar o container, use:

```bash
docker stop <container_id>
```



## Datasets

Os datasets utilizados neste projeto estão disponíveis publicamente no GitHub:

- [Dataset para Detecção (YOLOv5)](https://github.com/DiasDavi/semaforo-dataset-detector)
- [Dataset para Classificação (MobileNetV3)](https://github.com/DiasDavi/semaforo-dataset-classificador)

## Preparação dos Dados

- **YOLOv5**: A preparação dos dados foi realizada utilizando a plataforma [Roboflow](https://roboflow.com/).
- **MobileNetV3**: Um script personalizado foi utilizado para preparar e separar os dados para a classificação das fases semafóricas.

## API

### Endpoints Disponíveis

A aplicação Flask possui os seguintes endpoints:

- **GET /detect/config**  
  Retorna as configurações atuais do detector (IOU e confiança) como JSON.

- **POST /detect/config**  
  Atualiza as configurações do detector. Envie um JSON com os campos `iou` e `confidence`.

- **GET /classifier/config**  
  Retorna a configuração de confiança atual do classificador.

- **POST /classifier/config**  
  Atualiza a configuração de confiança do classificador. Envie um JSON com o campo `confidence`.

- **POST /detect**  
  Recebe uma imagem, realiza a detecção e retorna os resultados. Envie a imagem via `multipart/form-data`.

## Limitações Conhecidas

- O sistema atualmente suporta apenas imagens estáticas como entrada. Suporte para vídeos ou streams ainda não foi implementado.
- O desempenho dos modelos pode diminuir em situações complexas ou quando a visibilidade do semáforo está obstruída.

## Contribuições e Melhorias Futuras

- Melhorar a precisão em situações adversas, como clima severo ou obstruções parciais.
- Expandir o suporte para vídeos e streams em tempo real.

## Licença

Este projeto é distribuído sob a licença [MIT](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.

## Contato

Para dúvidas, sugestões ou feedback, entre em contato:

- **Autor**: Davi Dias e Giovanni Bortolosi
- **GitHub**: [github.com/DiasDavi](https://github.com/DiasDavi)



