import logging
import os
import time

from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)

from app.authentication import Authenticator
from app.collect_data import collect_data_from_dashboard
from app.dashboard_xpaths import DASHBOARD_XPATHS
from app.send_telegram_msg import send_informational_message

# Configuração do logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    logger.info(f'Iniciando processamento para o dashboard: {dashboard_name}')

    try:
        if initial_run:
            logger.info(
                f'Acessando o URL do {dashboard_name}: {dashboard_url}'
            )
            driver.get(dashboard_url)
            time.sleep(
                5
            )  # Espera para garantir o carregamento completo da página

            if dashboard_name == 'mvp1':
                logger.info(f'Iniciando autenticação para o {dashboard_name}')
                auth = Authenticator(driver)
                auth.authenticate()
                logger.info(
                    f'Autenticação concluída com sucesso para {dashboard_name}'
                )
            else:
                logger.info(
                    f'Dashboard {dashboard_name} não requer autenticação.'
                )
        else:
            logger.info(f'Recarregando o dashboard {dashboard_name}.')
            driver.refresh()
            time.sleep(5)

    except NoSuchElementException as e:
        logger.error(
            f'Elemento não encontrado durante o acesso ao {dashboard_name}: {e}'
        )
        return None
    except WebDriverException as e:
        logger.error(f'Erro de WebDriver ao acessar {dashboard_name}: {e}')
        return None
    except Exception as e:
        logger.error(
            f'Erro inesperado durante acesso ao {dashboard_name}: {e}'
        )
        return None

    try:
        logger.info(f'Iniciando coleta de dados para {dashboard_name}.')
        result = collect_data_from_dashboard(
            driver,
            dashboard_name,
            actions,
            browser_manager,
            download_path,
            initial_run=True,
        )

        if result:
            relatorio_path = result.get('relatorio_path')
            logger.info(
                f'Caminho do relatório para {dashboard_name}: {relatorio_path}'
            )

            if initial_run and relatorio_path:
                try:
                    logger.info(
                        f'Enviando mensagem informativa para {dashboard_name}.'
                    )
                    send_informational_message(
                        driver,
                        result['tme'],
                        result['tef'],
                        result['backlog'],
                        relatorio_path,
                        dashboard_name,
                    )
                    logger.info(
                        f'Mensagem enviada com sucesso para {dashboard_name}.'
                    )

                    # Remoção do arquivo após envio
                    logger.info(f'Removendo o arquivo {relatorio_path}.')
                    os.remove(relatorio_path)
                    logger.info(
                        f'Arquivo {relatorio_path} removido com sucesso.'
                    )
                except Exception as e:
                    logger.error(
                        f'Erro ao enviar mensagem ou remover arquivo: {e}'
                    )

            return result
        else:
            logger.error(f'Falha na coleta de dados para {dashboard_name}.')
            return None
    except Exception as e:
        logger.error(f'Erro durante o processamento do {dashboard_name}: {e}')
        return None
