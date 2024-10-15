import os
import time
from venv import logger

from action_manager import ActionManager
from browser import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

browser_manager = BrowserManager('data')
actions = ActionManager(browser_manager.driver)


def execute_download_actions(
    actions, browser_manager, download_path, dashboard_name
):
    """
    Executa uma sequência de ações para mover e interagir com elementos da página,
    realizar o download de um arquivo e renomeá-lo, e finaliza com o fechamento de um elemento.
    """

    def click_once(xpath, wait_time=25):
        try:
            # Espera até o elemento estar clicável
            element = WebDriverWait(browser_manager.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            time.sleep(1.5)
            element.click()
            logger.info(f'Elemento {xpath} clicado com sucesso.')
        except Exception as e:
            logger.error(f'Erro ao clicar no elemento {xpath}: {e}')
            raise

    # Aguardar a visibilidade do primeiro elemento e interagir
    WebDriverWait(browser_manager.driver, 25).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id=":rl:"]'))
    )
    time.sleep(0.5)
    actions.move_to_and_interact('//*[@id=":rl:"]', 'i')

    # Clicar nos elementos da sequência
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button'
    )
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label'
    )
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/label'
    )
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button'
    )

    logger.info('Ações para download concluídas')

    # Aguardar o download ser concluído
    file_path = wait_for_file_completion(download_path)
    if not file_path:
        logger.error(
            'Nenhum arquivo foi baixado ou tipo de arquivo inesperado.'
        )
        raise FileNotFoundError('Nenhum arquivo válido foi baixado.')

    # Renomear o arquivo com o nome do dashboard
    relatorio_filename = f'relatorio_{dashboard_name}.csv'
    relatorio_path = rename_latest_file(
        download_path, file_path, relatorio_filename
    )
    logger.info(
        f'Download concluído e arquivo renomeado para {relatorio_path}'
    )

    time.sleep(2)
    # Fechar o elemento após o download
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
    )
    time.sleep(0.5)
    return relatorio_path


def wait_for_file_completion(download_path, timeout=30):
    """
    Aguarda que o download seja concluído e o arquivo temporário seja convertido
    em um arquivo final (por exemplo, de ".part" ou com um nome aleatório).
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_path)
        for file_name in files:
            if not file_name.startswith('.') and file_name.endswith(
                ('.csv', '.xlsx')
            ):  # Adicione os formatos esperados
                return os.path.join(download_path, file_name)
        time.sleep(1)  # Espera um pouco antes de verificar novamente
    return None


def rename_latest_file(download_path, old_file_path, new_file_name):
    """
    Renomeia o arquivo mais recente baixado para um nome específico.
    """
    try:
        new_file_path = os.path.join(download_path, new_file_name)
        os.rename(old_file_path, new_file_path)
        return new_file_path
    except OSError as e:
        logger.error(f'Erro ao renomear o arquivo: {e}')
        raise
