import os
import time

from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class Authenticator:
    def __init__(self, driver):
        self.driver = driver

    def authenticate(self):
        load_dotenv()
        email = os.getenv('GRAFANA_USERNAME')
        password = os.getenv('GRAFANA_PASSWORD')
        login_url = 'https://e-bots.co/grafana/login'  # A URL de login pode ser diferente, ajuste se necessário
        self.driver.get(login_url)
        time.sleep(5)
        try:
            email_element = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[1]/div[2]/div/div/div/input')
            password_element = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[2]/div[2]/div/div/div/input')
            email_element.send_keys(email)
            password_element.send_keys(password)
            login_button = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/button')
            login_button.click()
            time.sleep(5)
        except NoSuchElementException as e:
            print(f'Erro ao encontrar elementos de login: {e}')
            self.driver.quit()

