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
    logger.info(f'Iniciando coleta de dados para o dashboard: {dashboard_name}')
    
    xpaths = DASHBOARD_XPATHS.get(dashboard_name)

    logger.info(f'XPaths encontrados: {xpaths}')

    if not xpaths:
        logger.error(f'Dashboard {dashboard_name} não encontrado!')
        return None

    try:
        if initial_run:
            logger.info(f'Primeira execução: acessando elementos do dashboard {dashboard_name}')
            actions.click_element(xpaths['var_exibir'])
            actions.click_element(xpaths['opcao_exibir'])
        
        # Verifica se o driver ainda está disponível
        if not driver:
            logger.error("WebDriver não está disponível! Reiniciando o navegador.")
            browser_manager.reiniciar_navegador()
            return None

        # Scroll até a tabela
        logger.info(f'Realizando scroll no dashboard {dashboard_name}')
        browser_manager.scroll_to_table()
        
        # Iniciar download se for a primeira execução
        if initial_run:
            logger.info(f'Iniciando download no dashboard {dashboard_name}')
            relatorio_path = execute_download_actions(
                actions, browser_manager, download_path, dashboard_name
            )
            if relatorio_path:
                logger.info(f'Relatório baixado com sucesso no caminho: {relatorio_path}')
            else:
                logger.warning(f'Falha no download do relatório para o dashboard {dashboard_name}')
        else:
            relatorio_path = None

        # Coletar KPIs
        logger.info(f'Coletando KPIs para o dashboard {dashboard_name}')
        tme_element = actions.find_element(xpaths['tme'])
        tme_xpath = tme_element.text if tme_element.text != 'No data' else '00:00:00'
        tef_element = actions.find_element(xpaths['tef'])
        tef_xpath = tef_element.text if tef_element.text != 'No data' else '00:00:00'
        backlog_xpath = actions.find_element(xpaths['backlog']).text
        
        logger.info(f'KPIs coletados: TME={tme_xpath}, TEF={tef_xpath}, Backlog={backlog_xpath}')

        return {
            'tme': tme_xpath,
            'tef': tef_xpath,
            'backlog': backlog_xpath,
            'relatorio_path': relatorio_path,
        }

    except NoSuchElementException as e:
        logger.error(f'Elemento não encontrado: {e}', exc_info=True)
        return None
    except WebDriverException as e:
        logger.error(f'Erro no WebDriver: {e}', exc_info=True)
        return None
    except Exception as e:
        logger.error(f'Erro inesperado: {e}', exc_info=True)
        return None

