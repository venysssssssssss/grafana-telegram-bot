# Usar uma imagem base do Python
FROM python:3.12-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instalar dependências necessárias para o Google Chrome e o ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3-dev \
    libx11-xcb1 \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    libasound2

# Baixar e instalar o Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || true \
    && apt-get -f install -y \
    && rm google-chrome-stable_current_amd64.deb

# Baixar e instalar o ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Definir o ChromeDriver no PATH
ENV PATH="/usr/local/bin/chromedriver:${PATH}"

# Copiar arquivos de dependências para o contêiner
COPY pyproject.toml poetry.lock ./

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências do projeto
RUN poetry install --no-root

# Copiar o código da aplicação
COPY . .

# Configurar a variável de ambiente para o caminho do Google Chrome
ENV PATH="/usr/bin/google-chrome:${PATH}"

# Comando para rodar a aplicação
CMD ["poetry", "run", "python", "app/main.py"]
