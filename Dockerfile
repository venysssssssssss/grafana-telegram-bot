# Usar uma imagem base do Python
FROM python:3.12-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar os arquivos de dependências para o contêiner
COPY pyproject.toml poetry.lock ./

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências do projeto
RUN poetry install --no-root

# Copiar o código da aplicação
COPY . .

# Configurar a variável de ambiente para o caminho do Chrome
ENV PATH="/usr/bin/google-chrome:${PATH}"

# Comando para rodar a aplicação
CMD ["poetry", "run", "python", "app/main.py"]
