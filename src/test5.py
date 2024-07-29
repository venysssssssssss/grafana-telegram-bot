import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Função para verificar e criar o diretório de download se necessário
def ensure_download_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# Função para iniciar o navegador Edge com diretório de download especificado
def start_browser():
    download_path = ensure_download_directory(os.path.join(os.getcwd(), 'data'))
    service = Service('edge/msedgedriver.exe')
    options = webdriver.EdgeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    driver = webdriver.Edge(service=service, options=options)
    driver.set_window_size(1366, 768)
    return driver

# Função para autenticar no site
def authenticate(driver, email, password):
    login_url = 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas'
    driver.get(login_url)
    time.sleep(5)
    try:
        email_element = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[1]/div[2]/div/div/div/input')
        password_element = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[2]/div[2]/div/div/div/input')
        email_element.send_keys(email)
        password_element.send_keys(password)
        login_button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/button')
        login_button.click()
        time.sleep(5)
    except NoSuchElementException as e:
        print(f'Erro ao encontrar elementos de login: {e}')
        driver.quit()

# Função para rolar a página até o final usando o scrollbar
def scroll_page_to_table(driver):
    try:
        scrollbar = driver.find_element(By.XPATH, '//*[@id="pageContent"]/div[3]/div/div[3]/div')
        action = ActionChains(driver)
        action.click_and_hold(scrollbar).perform()
        for _ in range(6):
            action.move_by_offset(0, 42).perform()
            time.sleep(0.1)
        action.release().perform()
    except NoSuchElementException as e:
        print(f'Erro ao encontrar o scrollbar: {e}')
        last_height = driver.execute_script('return document.body.scrollHeight')
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')
        while new_height != last_height:
            last_height = new_height
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = driver.execute_script('return document.body.scrollHeight')

# Função principal para testar a coleta de informações
def main():
    driver = start_browser()
    authenticate(driver, 'guilherme.caseiro@tahto.com.br', 'C453iro@102030.')
    scroll_page_to_table(driver)
    time.sleep(3)
    target_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id=":rl:"]')))
    action = ActionChains(driver)
    action.move_to_element(target_element).perform()
    time.sleep(2)
    action.send_keys('i').perform()
    dropdown_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button')))
    time.sleep(4)
    action.click(dropdown_element).perform()
    toggle_xlsx = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label')))
    time.sleep(0.5)
    action.click(toggle_xlsx).perform()
    download_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button')))
    time.sleep(0.5)
    action.click(download_button).perform()
    time.sleep(440)
    driver.quit()

# Executa a função principal
if __name__ == '__main__':
    main()
