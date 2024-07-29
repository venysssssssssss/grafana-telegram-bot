import os
import time

from authentication import authenticate
from browser import (clean_download_directory, rename_latest_file,
                     scroll_page_to_table, start_browser)
from data_processing import analyze_data
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():
    download_path = clean_download_directory('data')
    driver = start_browser(download_path)
    authenticate(driver, 'guilherme.caseiro@tahto.com.br', 'C453iro@102030.')
    scroll_page_to_table(driver)
    time.sleep(3)
    target_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id=":rl:"]'))
    )
    action = ActionChains(driver)
    action.move_to_element(target_element).perform()
    time.sleep(2)
    action.send_keys('i').perform()
    dropdown_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button',
            )
        )
    )
    time.sleep(4)
    action.click(dropdown_element).perform()
    toggle_xlsx = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label',
            )
        )
    )
    time.sleep(0.5)
    action.click(toggle_xlsx).perform()
    download_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button',
            )
        )
    )
    time.sleep(0.5)
    action.click(download_button).perform()
    time.sleep(
        8
    )  # Ajuste o tempo conforme necessário para garantir que o download seja concluído
    driver.quit()

    # Path to the downloaded CSV file
    rename_latest_file(download_path, 'relatorio.csv')
    metrics = analyze_data(os.path.join(download_path, 'relatorio.csv'))
    print('Returned metrics:', metrics)


if __name__ == '__main__':
    main()
