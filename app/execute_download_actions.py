import time
from venv import logger

from action_manager import ActionManager
from browser import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

browser_manager = BrowserManager('data')
actions = ActionManager(browser_manager.driver)


def execute_download_actions(actions, browser_manager, download_path):
    """
    Executa uma sequência de ações para mover e interagir com elementos da página,
    realizar o download de um arquivo e renomeá-lo, e finaliza com o fechamento de um elemento.
    """

    # Função para clicar em um elemento de forma garantida (somente 1 vez)
    def click_once(xpath, wait_time=15):
        try:
            # Espera até o elemento estar clicável
            element = WebDriverWait(browser_manager.driver, wait_time).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            # Clica no elemento
            time.sleep(1)
            element.click()
            logger.info(f'Elemento {xpath} clicado com sucesso.')
        except Exception as e:
            logger.error(f'Erro ao clicar no elemento {xpath}: {e}')
            raise

    # Espera até que o primeiro elemento esteja visível e interage
    WebDriverWait(browser_manager.driver, 25).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id=":rl:"]'))
    )
    actions.move_to_and_interact('//*[@id=":rl:"]', 'i')

    # Clicar nos elementos da sequência, garantindo que cada um seja clicado apenas uma vez
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

    # Aguarda o download ser concluído
    browser_manager.wait_for_download_complete(download_path)
    relatorio_path = browser_manager.rename_latest_file(
        download_path, 'relatorio.csv'
    )
    logger.info('Download concluído e arquivo renomeado')

    # Fechar o elemento após o download
    click_once(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
    )
    time.sleep(5)
    return relatorio_path
