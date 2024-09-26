# window_helper.py
import logging
import time

logger = logging.getLogger()


def switch_to_window(driver, window_index, dashboard_name):
    """
    Troca para a janela correta com base no índice e faz a verificação de troca.

    Args:
        driver (WebDriver): Instância do WebDriver.
        window_index (int): Índice da janela para alternar.
        dashboard_name (str): Nome do dashboard (MVP1 ou MVP3).
    """
    try:
        driver.switch_to.window(driver.window_handles[window_index])
        logger.info(f'Alternado para a janela do {dashboard_name}')
        time.sleep(5)  # Pequeno intervalo para garantir o carregamento
    except IndexError:
        logger.error(
            f'Não foi possível alternar para a janela {window_index} ({dashboard_name}).'
        )
    except Exception as e:
        logger.error(f'Erro ao alternar para a janela {dashboard_name}: {e}')
