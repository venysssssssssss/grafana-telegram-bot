import logging
import time
from queue import Queue
from threading import Lock, Thread

from fastapi import FastAPI, HTTPException

from app.action_manager import ActionManager
from app.browser import BrowserManager
from app.monitor_falhas import (iniciar_monitoramento, monitor_falhas,
                                pausar_monitoramento)
from app.process_dashboard import process_dashboard

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Inicializa FastAPI
app = FastAPI()

# Lock e fila para sincronizar acesso ao navegador
monitoramento_lock = Lock()
task_queue = Queue()

# URLs dos dashboards
dashboards = {
    'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/...',
    'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/...',
}

# Gerenciamento do navegador
browser_manager = BrowserManager('data')

driver_mvp1, driver_mvp3 = None, None  # Drivers iniciarão nulos até o monitoramento começar

# Thread de monitoramento
monitor_thread = None

def iniciar_monitoramento_thread():
    """Inicia a thread do monitoramento de falhas."""
    global monitor_thread
    if monitor_thread and monitor_thread.is_alive():
        logger.info("Monitoramento já está em execução.")
        raise HTTPException(status_code=400, detail="Monitoramento já iniciado.")

    # Inicializa os drivers e inicia a thread do monitoramento
    global driver_mvp1, driver_mvp3
    driver_mvp1, driver_mvp3 = browser_manager.driver, browser_manager.driver

    monitor_thread = Thread(
        target=monitor_falhas,
        args=(
            driver_mvp1,
            driver_mvp3,
            dashboards['mvp1'],
            dashboards['mvp3'],
            monitoramento_lock,
            task_queue,
        ),
        daemon=True
    )
    monitor_thread.start()
    logger.info("Monitoramento de falhas iniciado.")

def finalizar_monitoramento():
    """Finaliza a thread do monitoramento e encerra os drivers."""
    global driver_mvp1, driver_mvp3, monitor_thread

    if not monitor_thread or not monitor_thread.is_alive():
        logger.info("Nenhum monitoramento em execução.")
        raise HTTPException(status_code=400, detail="Nenhum monitoramento em execução.")

    logger.info("Finalizando monitoramento e encerrando drivers.")
    pausar_monitoramento()  # Pausa e encerra drivers
    driver_mvp1.quit()
    driver_mvp3.quit()
    driver_mvp1, driver_mvp3 = None, None

@app.get('/iniciar-monitoramento')
async def start_monitoring():
    """Endpoint para iniciar o monitoramento."""
    try:
        iniciar_monitoramento_thread()
        return {"message": "Monitoramento iniciado com sucesso."}
    except HTTPException as e:
        raise e

@app.get('/parar-monitoramento')
async def stop_monitoring():
    """Endpoint para parar o monitoramento."""
    try:
        finalizar_monitoramento()
        return {"message": "Monitoramento parado com sucesso."}
    except HTTPException as e:
        raise e

@app.get('/health')
async def health_check():
    """Verifica o status da aplicação."""
    return {'status': 'running'}

@app.post('/executar-coleta')
async def executar_coleta():
    """Executa a coleta de KPIs e pausa o monitoramento temporariamente."""
    try:
        with monitoramento_lock:
            logger.info("Pausando monitoramento para coleta de KPIs.")
            pausar_monitoramento()

            time.sleep(2)  # Espera para garantir que recursos foram liberados
            browser_manager.reiniciar_navegador()
            logger.info("Navegador reiniciado com sucesso.")

            # Coleta para MVP1
            kpis_mvp1 = process_dashboard(
                browser_manager.driver,
                'mvp1',
                dashboards['mvp1'],
                ActionManager(browser_manager.driver),
                browser_manager,
                browser_manager.clean_download_directory('data'),
                initial_run=True,
            )

            # Coleta para MVP3
            kpis_mvp3 = process_dashboard(
                browser_manager.driver,
                'mvp3',
                dashboards['mvp3'],
                ActionManager(browser_manager.driver),
                browser_manager,
                browser_manager.clean_download_directory('data'),
                initial_run=True,
            )

            return {
                "message": "Coleta executada com sucesso.",
                "kpis_mvp1": kpis_mvp1,
                "kpis_mvp3": kpis_mvp3,
            }

    except Exception as e:
        logger.error(f"Erro durante a coleta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar a coleta: {str(e)}")

    finally:
       logging.info("Reiniciando monitoramento após a coleta.")
