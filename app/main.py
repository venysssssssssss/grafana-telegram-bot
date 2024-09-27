import logging
import os
import time

from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from dashboard_xpaths import DASHBOARD_XPATHS
from execute_download_actions import execute_download_actions
from monitor_falhas import monitor_falhas
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from send_telegram_msg import send_informational_message
from window_helper import switch_to_window

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
            # Executar ações de download com o nome do dashboard
            relatorio_path = execute_download_actions(
                actions, browser_manager, download_path, dashboard_name
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
        
        # Garantir que o caminho correto do relatório está sendo processado para cada dashboard
        if result:
            relatorio_path = result['relatorio_path']  # Certifique-se de que este caminho é específico para cada dashboard

            # Enviar mensagem APENAS após garantir que o arquivo certo foi processado
            if initial_run and relatorio_path:
                send_informational_message(
                    driver,
                    result['tme'],
                    result['tef'],
                    result['backlog'],
                    relatorio_path,  # Caminho correto para cada dashboard
                    dashboard_name,
                )

                # Excluir o arquivo após enviar a mensagem
                logger.info(f'Removendo o arquivo {relatorio_path}')
                os.remove(relatorio_path)
                logger.info(f'Arquivo {relatorio_path} removido com sucesso.')

            return result
        else:
            logger.error(f'Falha ao coletar dados do {dashboard_name}')
            return None
    except Exception as e:
        logger.error(f'Erro ao processar o dashboard {dashboard_name}: {e}')
        return None


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
        logger.info('Processando MVP1...')
        kpis_mvp1 = process_dashboard(
            driver,
            'mvp1',
            dashboards['mvp1'],
            actions_mvp1,
            browser_manager,
            download_path,
            initial_run=True,
        )

        # Após concluir MVP1, vá para MVP3
        logger.info('Abrindo nova aba para MVP3...')
        driver.execute_script("window.open('');")
        switch_to_window(driver, 1, 'MVP3')  # Alternar para a aba do MVP3

        # Processar MVP3
        actions_mvp3 = ActionManager(driver)
        logger.info('Processando MVP3...')
        kpis_mvp3 = process_dashboard(
            driver,
            'mvp3',
            dashboards['mvp3'],
            actions_mvp3,
            browser_manager,
            download_path,
            initial_run=True,
        )

    except Exception as e:
        logger.error(f'Erro durante o processo principal: {e}')
    finally:
        driver.quit()
        logger.info('Todas as páginas foram acessadas e o navegador foi fechado.')

if __name__ == '__main__':
    main()
