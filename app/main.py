import logging
import os
import time
from queue import Queue
from threading import Lock, Thread

import schedule
from fastapi import FastAPI, HTTPException

from app.action_manager import ActionManager
from app.browser import BrowserManager
from app.monitor_falhas import (iniciar_monitoramento, monitor_falhas,
                                pausar_monitoramento)
from app.process_dashboard import process_dashboard

browser_manager = BrowserManager('data')

driver_mvp1 = browser_manager.driver
driver_mvp3 = browser_manager.driver

actions_mvp1 = ActionManager(driver_mvp1)
actions_mvp3 = ActionManager(driver_mvp3)

download_path = browser_manager.clean_download_directory('data')

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Lock e fila para sincronizar acesso ao navegador
monitoramento_lock = Lock()
task_queue = Queue()

# Inicializa FastAPI
app = FastAPI()

# URLs dos dashboards
dashboards = {
    'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/...',
    'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/...',
}

# Inicializar o navegador em uma única instância
browser_manager = BrowserManager(os.path.join(os.getcwd(), 'data'))
driver_mvp1 = browser_manager.driver
driver_mvp3 = browser_manager.driver


@app.on_event('startup')
def start_monitoring():
    """Inicia o monitoramento de falhas assim que o FastAPI é carregado."""
    logger.info('Iniciando o monitoramento no startup do FastAPI.')

    # Iniciando a thread do monitoramento, passando todos os argumentos
    monitor_falhas_thread = Thread(
        target=monitor_falhas,
        args=(
            driver_mvp1,
            driver_mvp3,
            dashboards['mvp1'],
            dashboards['mvp3'],
            monitoramento_lock,
            task_queue,
        ),
        daemon=True,  # A thread será encerrada junto com o processo principal
    )
    monitor_falhas_thread.start()
    logger.info('Monitoramento de falhas iniciado em thread separada.')


@app.on_event('shutdown')
def shutdown_event():
    """Evento de desligamento para limpar recursos."""
    driver_mvp1.quit()
    driver_mvp3.quit()
    logger.info('Navegadores fechados durante o desligamento.')


@app.get('/health')
async def health_check():
    """Verifica o status da aplicação."""
    return {'status': 'running'}


@app.post('/executar-coleta')
async def executar_coleta():
    """Executa a coleta de KPIs e pausa o monitoramento temporariamente."""
    try:
        with monitoramento_lock:
            pausar_monitoramento()
            browser_manager.reiniciar_navegador()
            logger.info('Monitoramento pausado para a coleta de KPIs.')

            kpis_mvp1 = process_dashboard(
                driver_mvp1,
                'mvp1',
                dashboards['mvp1'],
                actions_mvp1,
                browser_manager,
                download_path,
                initial_run=True,
            )

            # Executa a função process_dashboard para MVP3
            kpis_mvp3 = process_dashboard(
                driver_mvp3,
                'mvp3',
                dashboards['mvp3'],
                actions_mvp3,
                browser_manager,
                download_path,
                initial_run=True,
            )

            return {
                'message': 'Coleta executada com sucesso.',
                'kpis_mvp1': kpis_mvp1,
                'kpis_mvp3': kpis_mvp3,
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Erro ao executar a coleta: {e}'
        )
    finally:
        with monitoramento_lock:
            iniciar_monitoramento()
            logger.info('Monitoramento retomado após a coleta.')
