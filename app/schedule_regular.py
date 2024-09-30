import logging
import time

import schedule
from browser import BrowserManager
from execute_download_actions import execute_download_actions
from monitor_falhas import iniciar_monitoramento, pausar_monitoramento
from selenium.common.exceptions import WebDriverException
from send_telegram_msg import send_informational_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def download_and_send_message_for_dashboard(
    dashboard_name, driver, actions, browser_manager, kpi_data, download_path
):
    try:
        # Pausar monitoramento de falhas
        pausar_monitoramento()

        time.sleep(1)

        # Realiza o scroll e o download dos dados para o dashboard específico
        logger.info(f'Iniciando processo de download para {dashboard_name}')
        time.sleep(1)
        relatorio_path = execute_download_actions(
            actions, browser_manager, download_path, dashboard_name
        )
        logger.info(
            f'Relatório baixado para {dashboard_name} no caminho: {relatorio_path}'
        )

        # Envia a mensagem com as KPIs coletadas e o caminho do relatório
        send_informational_message(
            driver,
            kpi_data['tme'],
            kpi_data['tef'],
            kpi_data['backlog'],
            relatorio_path,
            dashboard_name,
        )
        logger.info(f'Mensagem enviada para o dashboard {dashboard_name}')

        # Aguardar 15 segundos antes de reiniciar o monitoramento
        time.sleep(15)

        # Reiniciar monitoramento de falhas
        iniciar_monitoramento()

    except WebDriverException as e:
        logger.error(
            f'Erro no WebDriver durante a coleta de dados no {dashboard_name}: {e}'
        )
        raise e


def download_and_send_message_for_mvp1(
    driver, actions_mvp1, browser_manager, kpis_mvp1
):
    try:
        # Limpa o diretório de downloads
        download_path = browser_manager.clean_download_directory('data')

        # Acessar o dashboard do MVP1
        logger.info('Acessando o dashboard MVP1')
        driver.get(
            'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas'
        )

        # Download e envio da mensagem
        download_and_send_message_for_dashboard(
            'MVP1',
            driver,
            actions_mvp1,
            browser_manager,
            kpis_mvp1,
            download_path,
        )

    except WebDriverException as e:
        logger.error(f'Erro no WebDriver ao tentar acessar MVP1: {e}')


def download_and_send_message_for_mvp3(
    driver, actions_mvp3, browser_manager, kpis_mvp3
):
    try:
        # Limpa o diretório de downloads
        download_path = browser_manager.clean_download_directory('data')

        # Acessar o dashboard do MVP3
        logger.info('Acessando o dashboard MVP3')
        driver.get(
            'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd'
        )

        # Download e envio da mensagem
        download_and_send_message_for_dashboard(
            'MVP3',
            driver,
            actions_mvp3,
            browser_manager,
            kpis_mvp3,
            download_path,
        )

    except WebDriverException as e:
        logger.error(f'Erro no WebDriver ao tentar acessar MVP3: {e}')


def schedule_for_day(day, times, func, *args):
    for time in times:
        logger.info(f'Agendando tarefa para {day} às {time}')
        getattr(schedule.every(), day).at(time).do(func, *args)


def schedule_regular_collections(
    driver, actions_mvp1, actions_mvp3, browser_manager, kpis_mvp1, kpis_mvp3
):
    """
    Configura o agendamento regular para os dashboards MVP1 e MVP3.
    """
    schedule_dict = {
        'monday': ['08:05', '13:11', '18:45', '20:05'],
        'tuesday': ['08:05', '12:05', '16:05', '20:05'],
        'wednesday': ['08:05', '12:05', '16:05', '20:05'],
        'thursday': ['08:05', '18:19', '16:05', '20:05'],
        'friday': ['08:05', '13:17', '17:11', '20:05'],
        'saturday': ['09:05', '12:05', '15:55'],
    }

    for day, times in schedule_dict.items():
        # Agendar MVP1
        schedule_for_day(
            day,
            times,
            download_and_send_message_for_mvp1,
            driver,
            actions_mvp1,
            browser_manager,
            kpis_mvp1,
        )

        # Agendar MVP3
        schedule_for_day(
            day,
            times,
            download_and_send_message_for_mvp3,
            driver,
            actions_mvp3,
            browser_manager,
            kpis_mvp3,
        )

    logger.info('Tarefas de agendamento configuradas')
