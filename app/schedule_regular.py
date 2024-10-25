import logging
import os
import time

import schedule
from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from collect_data import collect_data_from_dashboard
from execute_download_actions import execute_download_actions
from monitor_falhas import iniciar_monitoramento, pausar_monitoramento
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from send_telegram_msg import send_informational_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


dashboards = {
    'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas',
    'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd',
}


def download_and_send_message_for_dashboard(
    dashboard_name,
    driver,
    actions,
    browser_manager,
    kpi_data,
    download_path,
    initial_run=True,
):
    try:
        pausar_monitoramento()
        logger.info(f'Iniciando processo para o dashboard {dashboard_name}')

        # Obter a URL do dashboard a partir do dicionário
        dashboard_url = dashboards.get(dashboard_name.lower())
        if not dashboard_url:
            logger.error(f'URL não definida para {dashboard_name}')
            return  # Evita continuar sem uma URL válida

        logger.info(f'Acessando {dashboard_name} em {dashboard_url}')
        if initial_run:
            driver.get(dashboard_url)
            time.sleep(5)  # Aguardar carregamento do dashboard

            if dashboard_name.lower() == 'mvp1':
                auth = Authenticator(driver)
                auth.authenticate()
                logger.info(f'Autenticação concluída para {dashboard_name}')
        else:
            driver.refresh()
            time.sleep(5)  # Esperar recarregamento da página

        # Coletar e processar dados
        result = collect_data_from_dashboard(
            driver,
            dashboard_name,
            actions,
            browser_manager,
            download_path,
            initial_run,
        )

        if not result or not result.get('relatorio_path'):
            logger.error(f'Falha ao coletar dados do {dashboard_name}')
            return

        relatorio_path = result['relatorio_path']
        logger.info(
            f'Relatório baixado para {dashboard_name}: {relatorio_path}'
        )

        # Enviar mensagem com KPIs e caminho do relatório
        send_informational_message(
            driver,
            kpi_data['tme'],
            kpi_data['tef'],
            kpi_data['backlog'],
            relatorio_path,
            dashboard_name,
        )
        logger.info(f'Mensagem enviada para o dashboard {dashboard_name}')

        # Excluir o arquivo após o envio da mensagem
        if os.path.exists(relatorio_path):
            os.remove(relatorio_path)
            logger.info(f'Arquivo {relatorio_path} removido com sucesso.')

    except (WebDriverException, NoSuchElementException) as e:
        logger.error(
            f'Erro no WebDriver ou elemento não encontrado para {dashboard_name}: {e}'
        )
    except Exception as e:
        logger.error(f'Erro inesperado ao processar {dashboard_name}: {e}')
    finally:
        iniciar_monitoramento()
        logger.info(f'Monitoramento reiniciado para {dashboard_name}')


def execute_dashboard_task(
    driver, actions, browser_manager, kpis, dashboard_name, url
):
    try:
        # Verificar e reiniciar o navegador se necessário
        if not browser_manager.driver or not browser_manager.driver.session_id:
            logger.info('Iniciando uma nova sessão do navegador.')
            browser_manager.reiniciar_navegador()

        driver = browser_manager.driver  # Reutilizar a instância correta

        # Limpar o diretório de downloads
        download_path = browser_manager.clean_download_directory('data')

        # Acessar o dashboard
        logger.info(f'Acessando {dashboard_name} em {url}')
        driver.get(url)

        # Aguardar para garantir que o dashboard foi completamente carregado
        time.sleep(5)

        # Executar as ações de download e envio da mensagem
        download_and_send_message_for_dashboard(
            dashboard_name,
            driver,
            actions,
            browser_manager,
            kpis,
            download_path,
        )
    except WebDriverException as e:
        logger.error(f'Erro ao acessar {dashboard_name}: {e}')


def download_and_send_message_for_mvp1(
    driver, actions_mvp1, browser_manager, kpis_mvp1
):
    url = (
        'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/'
        'ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&'
        'var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas'
    )
    execute_dashboard_task(
        driver, actions_mvp1, browser_manager, kpis_mvp1, 'MVP1', url
    )


def download_and_send_message_for_mvp3(
    driver, actions_mvp3, browser_manager, kpis_mvp3
):
    url = (
        'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/'
        'ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&'
        'var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&'
        'from=now%2Fd&to=now%2Fd'
    )
    execute_dashboard_task(
        driver, actions_mvp3, browser_manager, kpis_mvp3, 'MVP3', url
    )


def schedule_for_day(day, times, func, *args):
    for time in times:
        logger.info(f'Agendando {func.__name__} para {day} às {time}')
        getattr(schedule.every(), day).at(time).do(func, *args)


def schedule_regular_collections(
    driver, actions_mvp1, actions_mvp3, browser_manager, kpis_mvp1, kpis_mvp3
):
    schedule_dict = {
        'monday': ['08:05', '12:05', '16:15', '20:05'],
        'tuesday': ['08:05', '12:05', '16:15', '20:05'],
        'wednesday': ['08:05', '12:05', '16:15', '20:05'],
        'thursday': ['08:05', '12:05', '16:15', '20:05'],
        'friday': ['08:05', '13:05', '16:15', '20:05'],
        'saturday': ['09:05', '12:05', '15:55'],
    }

    for day, times in schedule_dict.items():
        schedule_for_day(
            day,
            times,
            download_and_send_message_for_mvp1,
            driver,
            actions_mvp1,
            browser_manager,
            kpis_mvp1,
        )
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
