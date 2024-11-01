import logging
import time
import psutil
from queue import Queue
from threading import Lock, Thread

from fastapi import FastAPI, HTTPException

from app.action_manager import ActionManager
from app.browser import BrowserManager
from app.monitor_falhas import iniciar_monitoramento, monitor_falhas, pausar_monitoramento
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
    'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas',
    'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd',
}

# Gerenciamento do navegador
browser_manager = BrowserManager('data')

# Drivers iniciarão nulos até o monitoramento começar
driver_mvp1, driver_mvp3 = None, None

# Variável e sinalizador de controle do monitoramento
monitor_thread = None
monitoring_active = False  # Sinalização de controle do monitoramento


def encerrar_processos_residuais():
    """Encerra processos residuais do Chrome e ChromeDriver."""
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] in ['chrome', 'chromedriver']:
            try:
                proc.kill()
                logging.info(f'Processo {proc.info["name"]} (PID: {proc.info["pid"]}) encerrado.')
            except psutil.NoSuchProcess:
                pass


def iniciar_monitoramento_thread():
    """Inicia a thread do monitoramento de falhas."""
    global monitor_thread, monitoring_active, driver_mvp1, driver_mvp3

    # Verifica se já existe uma thread de monitoramento ativa
    if monitor_thread and monitor_thread.is_alive():
        logger.info('Monitoramento já está em execução.')
        raise HTTPException(
            status_code=400, detail='Monitoramento já iniciado.'
        )

    # Inicializa os drivers e ativa o monitoramento
    driver_mvp1 = browser_manager.driver
    driver_mvp3 = browser_manager.driver
    monitoring_active = True

    # Inicia a thread de monitoramento
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
        daemon=True,
    )
    monitor_thread.start()
    logger.info('Monitoramento de falhas iniciado.')


def finalizar_monitoramento():
    """Finaliza o monitoramento e encerra os drivers."""
    global driver_mvp1, driver_mvp3, monitor_thread, monitoring_active

    # Verifica se o monitoramento está ativo
    if not monitor_thread or not monitor_thread.is_alive():
        logger.info('Nenhum monitoramento em execução.')
        raise HTTPException(
            status_code=400, detail='Nenhum monitoramento em execução.'
        )

    # Desativa o monitoramento e registra a ação
    logger.info('Finalizando monitoramento e encerrando drivers.')
    monitoring_active = False  # Sinalização para finalizar o loop na thread

    # Encerra os drivers sem aguardar a finalização da thread
    browser_manager.encerrar_processos_chrome()
    driver_mvp1, driver_mvp3 = None, None

    # Aguarda a thread finalizar com timeout e redefine monitor_thread
    monitor_thread.join(timeout=5)
    monitor_thread = None  # Permite recriação ao reiniciar o monitoramento


@app.get('/iniciar-monitoramento')
async def start_monitoring():
    """Endpoint para iniciar o monitoramento."""
    try:
        iniciar_monitoramento_thread()
        return {'message': 'Monitoramento iniciado com sucesso.'}
    except HTTPException as e:
        raise e


@app.get('/parar-monitoramento')
async def stop_monitoring():
    """Endpoint para parar o monitoramento."""
    try:
        finalizar_monitoramento()
        return {'message': 'Monitoramento parado com sucesso.'}
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
            logger.info('Pausando monitoramento para coleta de KPIs.')
            pausar_monitoramento()

            time.sleep(2)  # Espera para garantir que recursos foram liberados
            browser_manager.reiniciar_navegador()
            logger.info('Navegador reiniciado com sucesso.')

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
                'message': 'Coleta executada com sucesso.',
                'kpis_mvp1': kpis_mvp1,
                'kpis_mvp3': kpis_mvp3,
            }

    except Exception as e:
        logger.error(f'Erro durante a coleta: {e}')
        raise HTTPException(
            status_code=500, detail=f'Erro ao executar a coleta: {str(e)}'
        )

    finally:
        logging.info('Reiniciando monitoramento após a coleta.')
        iniciar_monitoramento_thread()  # Reinicia o monitoramento após a coleta
