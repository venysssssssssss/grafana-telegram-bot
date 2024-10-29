import logging
import os
import time

from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)

from app.authentication import Authenticator
from app.collect_data import collect_data_from_dashboard
from app.dashboard_xpaths import DASHBOARD_XPATHS
from app.send_telegram_msg import send_informational_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


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
            if dashboard_name == 'mvp1' and 'login' in dashboard_url:
                auth = Authenticator(driver)
                auth.authenticate()
                logger.info(f'Autenticação concluída para {dashboard_name}')
            else:
                pass
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
            relatorio_path = result[
                'relatorio_path'
            ]  # Certifique-se de que este caminho é específico para cada dashboard

            # Enviar mensagem APENAS após garantir que o arquivo certo foi processado
            if initial_run and relatorio_path:
                logger.info('Relatorio path: %s', relatorio_path)

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
