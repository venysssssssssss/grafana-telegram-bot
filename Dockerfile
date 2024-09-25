FROM python:3.12-slim
 
RUN apt-get update && apt-get install -y 

# Adicione o repositório do Microsoft Edge
RUN wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main"

# Instale o Microsoft Edge
RUN apt-get update && \
    apt-get install -y microsoft-edge-stable

# Baixe e instale o EdgeDriver
RUN EDGE_VERSION=$(microsoft-edge --version | cut -d ' ' -f 3) && \
    wget -O /tmp/edgedriver.zip https://msedgedriver.azureedge.net/${EDGE_VERSION}/edgedriver_linux64.zip && \
    unzip /tmp/edgedriver.zip -d /tmp/ && \
    mkdir -p /usr/local/share/webdriver && \
    mv /tmp/msedgedriver /usr/local/share/webdriver/msedgedriver && \
    rm /tmp/edgedriver.zip

RUN pip install poetry


COPY app /src

WORKDIR /app

RUN poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]