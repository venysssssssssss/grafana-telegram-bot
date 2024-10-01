# Base image
FROM python:3.12-slim

# Instalar dependências necessárias e o GnuPG para gerenciar chaves GPG
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
    gnupg2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Instalar o Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Instalar o ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Definir o chromedriver no PATH
ENV PATH="/usr/local/bin/chromedriver:${PATH}"

# Copiar os arquivos do projeto para dentro do container
WORKDIR /app
COPY . .

# Instalar Poetry e dependências
RUN pip install poetry \
    && poetry install --no-root

# Comando para iniciar a aplicação
CMD ["poetry", "run", "python", "app/main.py"]
