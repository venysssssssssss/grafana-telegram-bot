import os
import time
import logging
from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from data_processing import DataProcessor
from monitor_falhas import monitor_falhas
from selenium.webdriver.common.by import By

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def main():
    logger.info("Iniciando o script principal")
    browser_manager = BrowserManager('data')
    download_path = browser_manager.clean_download_directory('data')
    try:
        time.sleep(4)
        actions = ActionManager(browser_manager.driver)
        auth = Authenticator(browser_manager.driver)
        auth.authenticate()
        logger.info("Autenticação concluída")

        # Coleta de KPIs adicionais
        actions.click_element('//*[@id="var-exibir"]')
        actions.click_element('//*[@id="options-exibir"]/li[4]/button')
        tme_element = actions.find_element(
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[5]/div/div/div[3]/div/div/div/div/div/div/span'
        )
        tme_xpath = tme_element.text if tme_element.text != 'No data' else '00:00:00'
        tef_element = actions.find_element(
            '//*[@id=":rj:"]/div/div/div/div/div/div/span'
        )
        tef_xpath = tef_element.text if tef_element.text != 'No data' else '00:00:00'
        backlog_xpath = actions.find_element(
            '//*[@id=":re:"]/div/div/div/div/div/div/span'
        ).text
        logger.info(f"KPIs coletados: TME={tme_xpath}, TEF={tef_xpath}, Backlog={backlog_xpath}")

        browser_manager.scroll_to_table()
        logger.info("Scroll até a tabela concluído")

        actions.move_to_and_interact('//*[@id=":rl:"]', 'i')
        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button'
        )
        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label'
        )
        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/label'
        )
        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button'
        )
        logger.info("Ações para download concluídas")

        # Aguarda o download ser concluído
        browser_manager.wait_for_download_complete(download_path)
        browser_manager.rename_latest_file(download_path, 'relatorio.csv')
        logger.info("Download concluído e arquivo renomeado")

        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
        )

        monitor_falhas(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath)
        logger.info("Monitoramento de falhas iniciado")

    finally:
        logger.info("Finalizando o script principal")

if __name__ == '__main__':
    main()
