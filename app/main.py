import logging
import os
import time

from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from dashboard_xpaths import DASHBOARD_XPATHS
from execute_download_actions import execute_download_actions
from monitor_falhas import monitor_falhas
from schedule_regular import schedule_regular_collections
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from send_telegram_msg import send_informational_message
from window_helper import switch_to_window  # Importar do novo arquivo

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def collect_data_from_dashboard(
    driver,
    dashboard_name,
    actions,
    browser_manager,
    download_path,
    initial_run=True,
):
    xpaths = DASHBOARD_XPATHS.get(dashboard_name)

    if not xpaths:
        logger.error(f'Dashboard {dashboard_name} não encontrado!')
        return None

    try:
        if initial_run:
            # Interagir com os elementos específicos do dashboard apenas na primeira vez
            actions.click_element(xpaths['var_exibir'])
            actions.click_element(xpaths['opcao_exibir'])

        # Scroll até a tabela - Executado sempre antes de coletar dados ou fazer download
        browser_manager.scroll_to_table()
        logger.info(f'Scroll até a tabela concluído para {dashboard_name}')

        if initial_run:
            # Executar ações de download apenas na primeira vez
            relatorio_path = execute_download_actions(
                actions, browser_manager, download_path
            )
            logger.info(
                f'Relatório baixado para o {dashboard_name} no caminho: {relatorio_path}'
            )
        else:
            relatorio_path = None

        # Coletar TME, TEF, e Backlog
        tme_element = actions.find_element(xpaths['tme'])
        tme_xpath = (
            tme_element.text if tme_element.text != 'No data' else '00:00:00'
        )

        tef_element = actions.find_element(xpaths['tef'])
        tef_xpath = (
            tef_element.text if tef_element.text != 'No data' else '00:00:00'
        )

        backlog_xpath = actions.find_element(xpaths['backlog']).text

        logger.info(
            f'KPIs coletados para {dashboard_name}: TME={tme_xpath}, TEF={tef_xpath}, Backlog={backlog_xpath}'
        )

        return {
            'tme': tme_xpath,
            'tef': tef_xpath,
            'backlog': backlog_xpath,
            'relatorio_path': relatorio_path,
        }
    except NoSuchElementException as e:
        logger.error(
            f'Elemento não encontrado durante a coleta de dados no {dashboard_name}: {e}'
        )
        return None
    except WebDriverException as e:
        logger.error(
            f'Erro no WebDriver durante a coleta de dados no {dashboard_name}: {e}'
        )
        return None
    except Exception as e:
        logger.error(
            f'Erro inesperado ao coletar dados do {dashboard_name}: {e}'
        )
        return None


def process_dashboard(
    driver,
    dashboard_name,
    dashboard_url,
    actions,
    browser_manager,
    download_path,
    initial_run=True,
):
    try:
        if initial_run:
            driver.get(dashboard_url)
            logger.info(f'Acessando o {dashboard_name}: {dashboard_url}')
            time.sleep(5)

            # Realizar autenticação somente para mvp1
            if dashboard_name == 'mvp1':
                auth = Authenticator(driver)
                auth.authenticate()
                logger.info(f'Autenticação concluída para {dashboard_name}')
        else:
            driver.refresh()
            time.sleep(5)

    except NoSuchElementException as e:
        logger.error(f'Erro de autenticação no {dashboard_name}: {e}')
        return
    except WebDriverException as e:
        logger.error(
            f'Erro de WebDriver ao tentar acessar {dashboard_name}: {e}'
        )
        return
    except Exception as e:
        logger.error(
            f'Erro inesperado ao tentar acessar {dashboard_name}: {e}'
        )
        return

    try:
        result = collect_data_from_dashboard(
            driver,
            dashboard_name,
            actions,
            browser_manager,
            download_path,
            initial_run,
        )
        if result:
            # Enviar mensagem após o download
            if result['relatorio_path']:
                send_informational_message(
                    driver,
                    result['tme'],
                    result['tef'],
                    result['backlog'],
                    result['relatorio_path'],
                    dashboard_name,
                )
            return result
        else:
            logger.error(f'Falha ao coletar dados do {dashboard_name}')
            return None
    except Exception as e:
        logger.error(f'Erro ao processar o dashboard {dashboard_name}: {e}')
        return None


def alternar_monitoramento(
    driver,
    dashboards,
    actions_mvp1,
    actions_mvp3,
    browser_manager,
    download_path,
):
    monitoramento_intervalo = 60  # 1 minuto para monitoramento em cada guia

    while True:
        # Monitorar MVP1 por 1 minuto
        logger.info('Alternando para o monitoramento de MVP1')
        switch_to_window(driver, 0, 'MVP1')  # Alternar para a aba do MVP1
        monitorar_por_tempo(
            driver,
            'mvp1',
            dashboards['mvp1'],
            actions_mvp1,
            browser_manager,
            download_path,
            monitoramento_intervalo,
        )

        # Monitorar MVP3 por 1 minuto
        logger.info('Alternando para o monitoramento de MVP3')
        switch_to_window(driver, 1, 'MVP3')  # Alternar para a aba do MVP3
        monitorar_por_tempo(
            driver,
            'mvp3',
            dashboards['mvp3'],
            actions_mvp3,
            browser_manager,
            download_path,
            monitoramento_intervalo,
        )


def monitorar_por_tempo(
    driver,
    dashboard_name,
    dashboard_url,
    actions,
    browser_manager,
    download_path,
    monitor_time,
):
    """
    Monitora o dashboard por um tempo definido e verifica falhas.
    """
    start_time = time.time()  # Marcar o início do monitoramento

    try:
        while (
            time.time() - start_time < monitor_time
        ):  # Executa o monitoramento durante o tempo definido
            result = process_dashboard(
                driver,
                dashboard_name,
                dashboard_url,
                actions,
                browser_manager,
                download_path,
                initial_run=False,
            )

            if result:
                # Executa o monitoramento de falhas
                monitor_falhas(driver_mvp1=driver, driver_mvp3=driver)
                logger.info(
                    f'Monitoramento de falhas finalizado para {dashboard_name}'
                )
            else:
                logger.error(
                    f'Falha ao coletar dados para {dashboard_name} durante o monitoramento'
                )

            # Aguarde um intervalo pequeno antes de verificar novamente
            time.sleep(
                5
            )  # Pequeno intervalo entre verificações para não sobrecarregar o monitoramento

    except Exception as e:
        logger.error(f'Erro ao monitorar o {dashboard_name}: {e}')


def main():
    # URLs e nomes dos dashboards MVP1 e MVP3
    dashboards = {
        'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas',
        'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd',
    }

    # Iniciar o navegador em uma única instância
    browser_manager = BrowserManager(os.path.join(os.getcwd(), 'data'))
    driver = browser_manager.driver
    download_path = browser_manager.clean_download_directory('data')

    try:
        # Processar MVP1
        actions_mvp1 = ActionManager(driver)
        kpis_mvp1 = process_dashboard(
            driver,
            'mvp1',
            dashboards['mvp1'],
            actions_mvp1,
            browser_manager,
            download_path,
            initial_run=True,
        )

        # Abrir uma nova aba para MVP3 na mesma sessão do navegador
        driver.execute_script("window.open('');")
        switch_to_window(driver, 1, 'MVP3')  # Alternar para a aba do MVP3

        # Processar MVP3
        actions_mvp3 = ActionManager(driver)
        kpis_mvp3 = process_dashboard(
            driver,
            'mvp3',
            dashboards['mvp3'],
            actions_mvp3,
            browser_manager,
            download_path,
            initial_run=True,
        )

        # Iniciar o monitoramento alternado
        logger.info(
            'Iniciando monitoramento alternado de falhas para MVP1 e MVP3'
        )
        schedule_regular_collections(
            driver,  # O driver principal, compartilhado entre os dashboards
            actions_mvp1,  # Ações específicas do MVP1
            actions_mvp3,  # Ações específicas do MVP3
            browser_manager,  # Gerenciador do navegador compartilhado
            kpis_mvp1,  # KPIs do MVP1
            kpis_mvp3,  # KPIs do MVP3
        )

        alternar_monitoramento(
            driver,
            dashboards,
            actions_mvp1,
            actions_mvp3,
            browser_manager,
            download_path,
        )

    except Exception as e:
        logger.error(f'Erro durante o processo principal: {e}')
    finally:
        driver.quit()
        logger.info(
            'Todas as páginas foram acessadas e o navegador foi fechado.'
        )


if __name__ == '__main__':
    main()
