import os
import shutil
import time

from selenium import webdriver
from selenium.webdriver.edge.service import Service


def ensure_download_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def clean_download_directory(directory):
    download_path = ensure_download_directory(
        os.path.join(os.getcwd(), directory)
    )
    for filename in os.listdir(download_path):
        file_path = os.path.join(download_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    return download_path


def start_browser(download_path):
    service = Service('edge/msedgedriver')
    options = webdriver.EdgeOptions()
    options.add_experimental_option(
        'prefs',
        {
            'download.default_directory': download_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True,
        },
    )
    driver = webdriver.Edge(service=service, options=options)
    driver.set_window_size(1366, 768)
    return driver


def scroll_page_to_table(driver):
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By

    try:
        scrollbar = driver.find_element(
            By.XPATH, '//*[@id="pageContent"]/div[3]/div/div[3]/div'
        )
        action = ActionChains(driver)
        action.click_and_hold(scrollbar).perform()
        for _ in range(6):
            action.move_by_offset(0, 42).perform()
            time.sleep(0.1)
        action.release().perform()
    except NoSuchElementException as e:
        print(f'Erro ao encontrar o scrollbar: {e}')
        last_height = driver.execute_script(
            'return document.body.scrollHeight'
        )
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')
        while new_height != last_height:
            last_height = new_height
            driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            time.sleep(2)
            new_height = driver.execute_script(
                'return document.body.scrollHeight'
            )


def rename_latest_file(download_path, new_name):
    time.sleep(
        5
    )  # Aguarde um tempo para garantir que o arquivo tenha sido baixado completamente
    files = os.listdir(download_path)
    if not files:
        raise FileNotFoundError('No files found in the download directory.')

    latest_file = max(
        [os.path.join(download_path, f) for f in files], key=os.path.getctime
    )
    base, ext = os.path.splitext(latest_file)
    if ext in [
        '.csv',
        '.xlsx',
    ]:  # Ajuste conforme necessário para os tipos de arquivo esperados
        new_path = os.path.join(download_path, new_name)
        os.rename(latest_file, new_path)
    else:
        raise ValueError(f'Unexpected file type: {ext}')
