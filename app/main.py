import os
import time
from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from data_processing import DataProcessor
from monitor_falhas import monitor_falhas
from send_telegram_msg import send_informational_message
from selenium.webdriver.common.by import By

def main():
    browser_manager = BrowserManager('data')
    download_path = browser_manager.clean_download_directory('data')
    try:
        time.sleep(4)
        actions = ActionManager(browser_manager.driver)
        auth = Authenticator(browser_manager.driver)
        auth.authenticate()
        # Collect additional KPIs
        actions.click_element('//*[@id="var-exibir"]')
        actions.click_element('//*[@id="options-exibir"]/li[4]/button')
        tme_element = actions.find_element(
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[5]/div/div/div[3]/div/div/div/div/div/div/span'
        )
        tme_xpath = (
            tme_element.text if tme_element.text != 'No data' else '00:00:00'
        )
        tef_element = actions.find_element(
            '//*[@id=":rj:"]/div/div/div/div/div/div/span'
        )
        tef_xpath = (
            tef_element.text if tef_element.text != 'No data' else '00:00:00'
        )
        backlog_xpath = actions.find_element(
            '//*[@id=":re:"]/div/div/div/div/div/div/span'
        ).text
        browser_manager.scroll_to_table()
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

        # Aguarda o download ser concluído
        browser_manager.wait_for_download_complete(download_path)
        browser_manager.rename_latest_file(download_path, 'relatorio.csv')
        

        actions.click_element(
            '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
        )

        #send_informational_message(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath)

        #time.sleep(10)

        monitor_falhas(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath)

    finally:
        browser_manager.quit_browser()

if __name__ == '__main__':
    main()
