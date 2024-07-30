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
    login_url = 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp2&orgId=1&refresh=5m&var-Robot_id=82&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas'
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


def scroll_table_to_bottom(driver):
    all_data = []
    total_rows_counted = 0  # Inicializa o contador de linhas

    for _ in range(4):  # Realiza a rolagem 3 vezes
        try:
            # Espera até que o elemento do scrollbar esteja visível
            scrollbar = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id=":rm:"]/div/div/div[3]/div')
                )
            )
            action = ActionChains(driver)
            action.click_and_hold(scrollbar).perform()

            # Move o scrollbar para baixo
            action.move_by_offset(
                0, 20
                0, 100
            ).perform()  # Ajuste este valor conforme necessário
            action.release().perform()

            # Coletar dados após cada rolagem
            base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
            rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
            new_rows_count = len(rows) - total_rows_counted
            total_rows_counted += (
                new_rows_count  # Atualiza o contador total de linhas
            )

<<<<<<< HEAD
            # Coleta as informações das novas linhas
=======
>>>>>>> 286f0fca5436743759c6810d802ddac182e410d8
            for row in range(
                total_rows_counted - new_rows_count + 1, total_rows_counted + 1
            ):
                try:
<<<<<<< HEAD
                    item_xpath = f'{base_xpath}[{row+1}]/div[3]'
                    status_xpath = f'{base_xpath}[{row+1}]/div[7]'
=======
                    rows = driver.find_elements(By.XPATH, f'{base_xpath}')
                    rows += rows
                    item_xpath = f'{base_xpath}[{row}]/div[3]'
                    status_xpath = f'{base_xpath}[{row}]/div[7]'
>>>>>>> 286f0fca5436743759c6810d802ddac182e410d8

                    item = driver.find_element(By.XPATH, item_xpath).text
                    status = driver.find_element(By.XPATH, status_xpath).text
                    time.sleep(1)
                    all_data.append({'item': item, 'status': status})
                    print(len(rows))
                    print(len(all_data))
                except NoSuchElementException:
                    continue

        except TimeoutException as e:
            print(f'Tempo esgotado ao esperar pelo scrollbar: {e}')
            break

    return all_data


# Função para coletar informações do site
def collect_info(driver):
    try:
        all_data = scroll_table_to_bottom(driver)
        total_rows = len(all_data)

        base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
        count_success = 0
        count_business_error = 0
        count_system_failure = 0
        falha_detectada = False

        # Coleta os valores dos XPaths adicionais
        tme_xpath = driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[5]/div/div/div[3]/div/div/div/div/div/div/span',
        ).text
        tef_xpath = driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[6]/div/div/div[3]/div/div/div/div/div/div/span',
        ).text
        backlog_xpath = driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div/div[3]/div/div/div/div/div/div/span',
        ).text

        for data in all_data:
            item = data['item']
            status = data['status']

            if (
                item == 'ValidarVendasLiberadas'
                and status == 'Falha de sistema'
            ):
                falha_detectada = True

            if (
                status == 'Concluído com sucesso'
                and item != 'ValidarVendasLiberadas'
            ):
                count_success += 1
            elif (
                status == 'Erro de negócio'
                and item != 'ValidarVendasLiberadas'
            ):
                count_business_error += 1
            elif (
                status == 'Falha de sistema'
                and item != 'ValidarVendasLiberadas'
            ):
                count_system_failure += 1

        # Exibir a quantidade total de linhas processadas no terminal
        print(f'Total de linhas processadas: {total_rows}')

        return (
            count_success,
            count_business_error,
            count_system_failure,
            falha_detectada,
            tme_xpath,
            tef_xpath,
            backlog_xpath,
            total_rows,
        )

    except WebDriverException as e:
        print(f'Erro ao coletar informações: {e}')
        return None, None, None, None, None, None, None, None


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

    # Rolar a página inteira e a tabela interna até o final após a autenticação
    scroll_to_bottom(driver)
    time.sleep(1)

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
