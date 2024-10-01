# Use a imagem base oficial do Python
FROM python:3.12-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo pyproject.toml e poetry.lock para o diretório de trabalho
COPY pyproject.toml poetry.lock /app/

# Instale o Poetry
RUN pip install poetry

# Instale as dependências da aplicação usando o Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copie o restante da aplicação para o container
COPY . /app

# Comando para rodar a aplicação
CMD ["poetry", "run", "python", "app/main.py"]
