import os
import time
import logging
from action_manager import ActionManager
from send_telegram_msg import send_informational_message
from authentication import Authenticator
from browser import BrowserManager
from data_processing import DataProcessor
from monitor_falhas import monitor_falhas
from selenium.webdriver.common.by import By
from data_processing import DataProcessor
from execute_download_actions import execute_download_actions

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

        relatorio_path = execute_download_actions(actions, browser_manager, download_path)

        
        #send_informational_message(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath, relatorio_path)

        #time.sleep(200)

        monitor_falhas(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath, actions, browser_manager)
        logger.info("Monitoramento de falhas finalizado")

    finally:
        logger.info("Finalizando o script principal")

if __name__ == '__main__':
    main()
