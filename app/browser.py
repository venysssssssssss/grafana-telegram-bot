import logging
import os
import shutil
import time

import psutil
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


class BrowserManager:
    def __init__(self, download_directory='data'):
        self.download_directory = self.clean_download_directory(
            download_directory
        )
        self.driver = None  # Inicializa sem instância do navegador
        self.start_browser()

    def start_browser(self):
        """Inicia uma nova instância do navegador."""
        self.encerrar_processos_chrome()  # Garante que processos anteriores estão encerrados

        driver_path = os.path.join(os.getcwd(), '/usr/local/bin/chromedriver')
    def __init__(self, download_directory):
        self.download_directory = os.path.join(os.getcwd(), download_directory)
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        self.driver = self.start_browser(self.download_directory)

    def start_browser(self, download_path):
        driver_path = os.path.join(
            os.getcwd(), '/usr/local/bin/chromedriver'
        )  # Corrigido caminho absoluto para o chromedriver

        self.encerrar_processos_chrome()

        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--timeout=300')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1366,1080')
        # options.add_argument('--headless')
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
                'download.default_directory': self.download_directory,
                'download.prompt_for_download': False,
                'safebrowsing.enabled': True,
            },
        )

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)
            logger.info('Navegador iniciado com sucesso.')
        except WebDriverException as e:
            logger.error(f'Erro ao iniciar o navegador: {e}')
            raise

    def reiniciar_navegador(self):
        """Reinicia o navegador garantindo que todos os processos sejam encerrados."""
        try:
            self.fechar_navegador()
            self.start_browser('data')
        except Exception as e:
            logger.error(f'Erro ao reiniciar o navegador: {e}')
            raise

    def fechar_navegador(self):
        """Fecha o navegador e limpa os processos relacionados."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info('Navegador fechado.')
        except Exception as e:
            logger.error(f'Erro ao fechar o navegador: {e}')
        finally:
            self.encerrar_processos_chrome()

    def encerrar_processos_chrome(self):
        """Encerra todos os processos do Chrome e Chromedriver."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if (
                    'chrome' in proc.info['name'].lower()
                    or 'chromedriver' in proc.info['name'].lower()
                ):
                    psutil.Process(proc.info['pid']).kill()
                    logger.info(f'Processo {proc.info["name"]} encerrado.')
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                pass

    def scroll_to_table(self):
        """Executa o scroll até a tabela alvo."""
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
            logger.info('Scroll realizado com sucesso.')
        except NoSuchElementException as e:
            logger.error(f'Erro ao encontrar o scrollbar: {e}')
            self.scroll_until_bottom()

    def scroll_until_bottom(self):
        """Scroll até o final da página caso o scrollbar não seja encontrado."""
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
        """Limpa o diretório de downloads."""
        download_path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        for filename in os.listdir(download_path):
            file_path = os.path.join(download_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                logger.info(f'Arquivo {file_path} removido.')
            except Exception as e:
                logger.error(f'Erro ao remover {file_path}: {e}')
        return download_path

    def wait_for_download_complete(self, timeout=60):
        """Espera até que o download seja concluído."""
        start_time = time.time()
        while True:
            files = [
                f
                for f in os.listdir(self.download_directory)
                if not f.endswith('.crdownload')
            ]
            if files:
                return max(
                    [os.path.join(self.download_directory, f) for f in files],
                    key=os.path.getctime,
                )
            elif time.time() - start_time > timeout:
                raise TimeoutError(
                    'Tempo excedido para conclusão do download.'
                )
            time.sleep(1)

    def rename_latest_file(self, new_name):
        """Renomeia o arquivo mais recente no diretório de downloads."""
        try:
            latest_file = self.wait_for_download_complete()
            base, ext = os.path.splitext(latest_file)
            if ext in ['.csv', '.xlsx']:
                new_path = os.path.join(self.download_directory, new_name)
                os.rename(latest_file, new_path)
                logger.info(f'Arquivo renomeado para {new_path}.')
            else:
                raise ValueError(f'Tipo de arquivo inesperado: {ext}')
        except Exception as e:
            logger.error(f'Erro ao renomear o arquivo: {e}')
            raise

    def navegar_para_url(self, url):
        """Navega para a URL especificada."""
        try:
            if not self.driver:
                self.start_browser()
            self.driver.get(url)
            logger.info(f'Acessando URL: {url}')
        except WebDriverException as e:
            logger.error(f'Erro ao acessar {url}: {e}')
            self.reiniciar_navegador()

    def quit(self):
        """Fecha o navegador e limpa os processos."""
        self.fechar_navegador()
        self.driver = None
