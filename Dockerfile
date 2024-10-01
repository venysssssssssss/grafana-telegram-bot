# Base image
FROM python:3.12-slim

# Instalar dependências necessárias
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
    libasound2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxtst6 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxrandr2 \
    libxss1 \
    --no-install-recommends \
    gnupg2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Baixar e instalar o Google Chrome da URL fornecida
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome-linux64.zip -d /opt/ \
    && rm /tmp/chrome-linux64.zip \
    && ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome

# Baixar e instalar o ChromeDriver da URL fornecida
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm /tmp/chromedriver-linux64.zip

# Definir permissões de execução para o Chrome e ChromeDriver
RUN chmod +x /usr/bin/google-chrome /usr/local/bin/chromedriver

# Definir variáveis de ambiente necessárias
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Copiar os arquivos do projeto para dentro do container
WORKDIR /app
COPY . .

# Instalar Poetry e dependências
RUN pip install poetry \
    && poetry install --no-root

# Comando para iniciar a aplicação
CMD ["poetry", "run", "python", "app/main.py"]
