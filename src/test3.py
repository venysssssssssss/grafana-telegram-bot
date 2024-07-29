import time

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Função para iniciar o navegador Edge
def start_browser():
    service = Service(
        'edge/msedgedriver'
    )  # Substitua pelo caminho correto do EdgeDriver
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(service=service, options=options)
    driver.set_window_size(1366, 768)  # Define o tamanho da janela
    return driver


# Função para autenticar no site
def authenticate(driver, email, password):
    login_url = 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp2&orgId=1&refresh=5m&var-Robot_id=82&var-exibir_itens=processados&var-exibir=100&var-exibir_tarefas=todas'
    driver.get(login_url)
    time.sleep(5)

    try:
        email_element = driver.find_element(
            By.XPATH,
            '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[1]/div[2]/div/div/div/input',
        )
        password_element = driver.find_element(
            By.XPATH,
            '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[2]/div[2]/div/div/div/input',
        )

        email_element.send_keys(email)
        password_element.send_keys(password)

        login_button = driver.find_element(
            By.XPATH,
            '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/button',
        )
        login_button.click()

        # Aguarda o login ser processado e a nova página carregar
        time.sleep(5)
    except NoSuchElementException as e:
        print(f'Erro ao encontrar elementos de login: {e}')
        driver.quit()


# Função para rolar a página até o final usando o scrollbar
def scroll_to_bottom(driver):
    try:
        wait_for_element_and_click(
            driver,
            '//*[@id="reactRoot"]/div[1]/div/div[1]/div[2]/div[2]/div[4]/div/div[1]/button[1]',
        )
        wait_for_element_and_click(
            driver, '//*[@id="TimePickerContent"]/div/div/div[1]/div/div/input'
        )
        send_keys_to_element(
            driver,
            '//*[@id="TimePickerContent"]/div/div/div[1]/div/div/input',
            '1',
        )
        wait_for_element_and_click(
            driver,
            '//*[@id="TimePickerContent"]/div/div/div[2]/div[1]/ul/li[4]/label',
        )

        scrollbar = driver.find_element(
            By.XPATH, '//*[@id="pageContent"]/div[3]/div/div[3]/div'
        )
        action = ActionChains(driver)
        action.click_and_hold(scrollbar).perform()

        for _ in range(6):
            action.move_by_offset(
                0, 50
            ).perform()  # Ajuste o valor do offset se necessário
            time.sleep(1)

        action.release().perform()
    except NoSuchElementException as e:
        print(f'Erro ao encontrar o scrollbar: {e}')

    # Verificação para garantir que a rolagem esteja completa
    last_height = driver.execute_script('return document.body.scrollHeight')
    time.sleep(2)
    new_height = driver.execute_script('return document.body.scrollHeight')
    while new_height != last_height:
        last_height = new_height
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);'
        )
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')


# Função para rolar a tabela até o final usando JavaScript
def scroll_table_to_bottom(driver):
    all_data = []
    total_rows_counted = 0
    previous_rows_counted = -1

    target_xpath = (
        '//*[@id=":rl:"]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div[1]'
    )

    while total_rows_counted != previous_rows_counted:
        previous_rows_counted = total_rows_counted

        driver.execute_script(
            'arguments[0].scrollBy(0, arguments[0].scrollHeight);',
            driver.find_element(By.XPATH, target_xpath),
        )
        time.sleep(1)  # Aguarda o carregamento de novas linhas

        rows = driver.find_elements(By.XPATH, target_xpath)
        new_rows_count = len(rows) - total_rows_counted
        total_rows_counted += new_rows_count

        for row in range(
            total_rows_counted - new_rows_count + 1, total_rows_counted + 1
        ):
            try:
                item_xpath = f'{target_xpath}[{row}]'
                item = driver.find_element(By.XPATH, item_xpath).text
                all_data.append(item)
            except NoSuchElementException:
                continue

    return all_data


# Função para coletar informações do site
def collect_info(driver):
    try:
        all_data = scroll_table_to_bottom(driver)
        total_rows = len(all_data)

        print(f'Total de linhas processadas: {total_rows}')
        for item in all_data:
            print(item)

        return all_data

    except WebDriverException as e:
        print(f'Erro ao coletar informações: {e}')
        return None


def wait_for_element_and_click(driver, xpath, timeout=10):
    for _ in range(timeout):
        try:
            element = driver.find_element(By.XPATH, xpath)
            element.click()
            return
        except NoSuchElementException:
            time.sleep(1)
    raise NoSuchElementException(f'Elemento não encontrado: {xpath}')


def send_keys_to_element(driver, xpath, keys, timeout=10):
    for _ in range(timeout):
        try:
            element = driver.find_element(By.XPATH, xpath)
            element.send_keys(keys)
            return
        except NoSuchElementException:
            time.sleep(1)
    raise NoSuchElementException(f'Elemento não encontrado: {xpath}')


# Função principal para testar a coleta de informações
def main():
    driver = start_browser()
    authenticate(driver, email, password)

    scroll_to_bottom(driver)

    # Coletar informações e imprimir a quantidade de linhas processadas
    collect_info(driver)
    time.sleep(20)
    driver.quit()


# Credenciais de login
email = 'guilherme.caseiro@tahto.com.br'
password = 'C453iro@102030.'

# Executa a função principal
if __name__ == '__main__':
    main()
