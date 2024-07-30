import os
import time
from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from data_processing import DataProcessor
from send_telegram_msg import send_informational_message
from selenium.webdriver.common.by import By

def main():
    browser_manager = BrowserManager('data')
    download_path = browser_manager.clean_download_directory('data')
    actions = ActionManager(browser_manager.driver)
    auth = Authenticator(browser_manager.driver)
    auth.authenticate()
    # Collect additional KPIs
    tme_xpath = actions.find_element(
        '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[5]/div/div/div[3]/div/div/div/div/div/div/span'
    ).text
    tef_xpath = actions.find_element(
        '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[6]/div/div/div[3]/div/div/div/div/div/div/span'
    ).text
    backlog_xpath = actions.find_element(
        '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div/div[3]/div/div/div/div/div/div/span'
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
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button'
    )

    # Aguarda o download ser concluído
    browser_manager.wait_for_download_complete(download_path)
    browser_manager.rename_latest_file(download_path, 'relatorio.csv')
    data_processor = DataProcessor(
        os.path.join(download_path, 'relatorio.csv')
    )
    metrics = data_processor.analyze_data()
    print('Returned metrics:', metrics)

    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
    )

    send_informational_message(metrics, tme_xpath, tef_xpath, backlog_xpath)

    time.sleep(500)
    browser_manager.driver.quit()


if __name__ == '__main__':
    main()
