import os
import time
from browser import BrowserManager
from authentication import Authenticator
from data_processing import DataProcessor
from action_manager import ActionManager


def main():
    browser_manager = BrowserManager('data')
    download_path = browser_manager.clean_download_directory('data')

    auth = Authenticator(browser_manager.driver)
    auth.authenticate()
    browser_manager.scroll_to_table()
    actions = ActionManager(browser_manager.driver)

    actions.move_to_and_interact('//*[@id=":rl:"]', 'i')
    actions.click_element('//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button')
    actions.click_element('//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label')
    actions.click_element('//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button')

    # Aguarda o download ser concluído
    browser_manager.wait_for_download_complete(download_path)
    browser_manager.rename_latest_file(download_path, 'relatorio.csv')

    data_processor = DataProcessor(os.path.join(download_path, 'relatorio.csv'))
    metrics = data_processor.analyze_data()
    print('Returned metrics:', metrics)

    browser_manager.driver.quit()

if __name__ == '__main__':
    main()

