import logging
import time

import schedule
from browser import BrowserManager  # Importação para reinicializar o navegador
from execute_download_actions import execute_download_actions
from selenium.common.exceptions import WebDriverException
from send_telegram_msg import send_informational_message
from window_helper import switch_to_window

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def download_and_send_message_for_dashboard(
    dashboard_name, driver, actions, browser_manager, kpi_data, download_path
):
    try:
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

    except WebDriverException as e:
        logger.error(
            f'Erro no WebDriver durante a coleta de dados no {dashboard_name}: {e}'
        )
        raise e


def download_and_send_message_for_both_dashboards(
    driver, actions_mvp1, actions_mvp3, browser_manager, kpis_mvp1, kpis_mvp3
):
    try:
        # Limpa o diretório de downloads e reseta as variáveis de controle
        download_path = browser_manager.clean_download_directory('data')

        # Alternar para a guia do MVP1
        switch_to_window(driver, 0, 'MVP1')
        download_and_send_message_for_dashboard(
            'MVP1',
            driver,
            actions_mvp1,
            browser_manager,
            kpis_mvp1,
            download_path,
        )

        # Alternar para a guia do MVP3
        switch_to_window(driver, 1, 'MVP3')
        download_and_send_message_for_dashboard(
            'MVP3',
            driver,
            actions_mvp3,
            browser_manager,
            kpis_mvp3,
            download_path,
        )

    except WebDriverException as e:
        logger.error(
            f'Erro no WebDriver ao tentar acessar MVP: {e}'
        )   # type: ignore


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
        'monday': ['08:05', '12:05', '16:05', '20:05'],
        'tuesday': ['08:05', '12:05', '16:05', '20:05'],
        'wednesday': ['08:05', '12:05', '16:05', '20:05'],
        'thursday': ['08:05', '18:19', '16:05', '20:05'],
        'friday': ['08:05', '13:17', '17:11', '20:05'],
        'saturday': ['09:05', '12:05', '15:55'],
    }

    for day, times in schedule_dict.items():
        schedule_for_day(
            day,
            times,
            download_and_send_message_for_both_dashboards,
            driver,
            actions_mvp1,
            actions_mvp3,
            browser_manager,
            kpis_mvp1,
            kpis_mvp3,
        )

    logger.info('Tarefas de agendamento configuradas')
