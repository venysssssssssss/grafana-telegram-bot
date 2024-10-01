import os
import shutil
import time

from selenium import webdriver
from selenium.common.exceptions import \
    NoSuchElementException  # Import necessário
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class BrowserManager:
    def __init__(self, download_directory):
        self.download_directory = os.path.join(os.getcwd(), download_directory)
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        self.driver = self.start_browser(self.download_directory)

    def start_browser(self, download_path):
        driver_path = os.path.join(
            os.getcwd(), '/usr/local/bin/chromedriver'
        )  # Corrigido caminho absoluto para o chromedriver

        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Comentado para desativar o modo headless
        options.add_argument(
            '--no-sandbox'
        )  # Adicionado para evitar problemas de sandbox
        options.add_argument(
            '--disable-dev-shm-usage'
        )  # Adicionado para evitar problemas de memória compartilhada
        options.add_argument(
            '--disable-gpu'
        )  # Adicionado para evitar problemas com GPU
        options.add_argument('--window-size=1366,1080')  # Tamanho da janela

        options.add_experimental_option(
            'prefs',
            {
                'download.default_directory': download_path,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True,
            },
        )
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def scroll_to_table(self):
        try:
            scrollbar = self.driver.find_element(
                By.XPATH, '//*[@id="pageContent"]/div[3]/div/div[3]/div'
            )
            action = ActionChains(self.driver)
            action.click_and_hold(scrollbar).perform()
            for _ in range(6):
                action.move_by_offset(0, 42).perform()
                time.sleep(0.1)
            action.release().perform()
        except NoSuchElementException as e:
            print(f'Erro ao encontrar o scrollbar: {e}')
            last_height = self.driver.execute_script(
                'return document.body.scrollHeight'
            )
            new_height = last_height
            while new_height == last_height:
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);'
                )
                time.sleep(2)
                new_height = self.driver.execute_script(
                    'return document.body.scrollHeight'
                )

    def clean_download_directory(self, directory):
        download_path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        for filename in os.listdir(download_path):
            file_path = os.path.join(download_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        return download_path

    def wait_for_download_complete(self, download_path, timeout=60):
        start_time = time.time()
        while True:
            files = [
                f
                for f in os.listdir(download_path)
                if not f.endswith('.crdownload')
            ]
            if files:
                return max(
                    [os.path.join(download_path, f) for f in files],
                    key=os.path.getctime,
                )
            elif time.time() - start_time > timeout:
                raise TimeoutError(
                    'Timed out waiting for the file to download.'
                )
            time.sleep(1)  # Verifica a cada segundo

    def rename_latest_file(self, download_path, new_name):
        latest_file = self.wait_for_download_complete(download_path)
        base, ext = os.path.splitext(latest_file)
        if ext in ['.csv', '.xlsx']:
            new_path = os.path.join(download_path, new_name)
            os.rename(latest_file, new_path)
        else:
            raise ValueError(f'Unexpected file type: {ext}')

    def quit(self):
        self.driver.quit()
