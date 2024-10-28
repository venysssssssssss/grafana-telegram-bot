import logging

from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)

from app.dashboard_xpaths import DASHBOARD_XPATHS
from app.execute_download_actions import execute_download_actions

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
