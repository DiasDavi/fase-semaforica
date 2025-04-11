# Use a imagem base do Python 3.8
FROM python:3.8-slim

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expõe a porta 5000
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "app.py"]