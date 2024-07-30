import datetime
import threading
import time

import requests
import schedule
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Função para iniciar o navegador Edge
def start_browser():
    service = Service(
        'edge/msedgedriver.exe'
    )  # Substitua pelo caminho correto do EdgeDriver
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(service=service, options=options)
    driver.set_window_size(1366, 768)  # Define o tamanho da janela
    return driver


# Função para autenticar no site
def authenticate(driver, email, password):
    login_url = 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&var-Robot=tahto-pap-mvp2&var-Robot_id=82&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now&refresh=30s'
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


# Função para enviar mensagem via Telegram
def send_telegram_message(message):
    telegram_token = '7226155746:AAEBPeOtzJrD_KQyeZinNBjh5HMmvHTBZLs'  # Substitua pelo token do seu bot do Telegram
    chat_id = '-1002165188451'  # Substitua pelo seu chat ID
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)


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
    try:
        while True:
            try:
                # Espera até que o elemento do scrollbar esteja visível
                scrollbar = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id=":rm:"]/div/div/div[3]/div')
                    )
                )
            except TimeoutException:
                print(
                    'Tempo esgotado ao esperar pelo scrollbar. Tentando novamente...'
                )
                continue

            action = ActionChains(driver)
            action.click_and_hold(scrollbar).perform()

            for _ in range(1):
                action.move_by_offset(
                    0, 50
                ).perform()  # Ajuste o valor do offset se necessário
                time.sleep(1)

            action.release().perform()

            # Coletar dados durante a rolagem
            base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
            rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
            for row in rows:
                try:
                    item_xpath = row.find_element(By.XPATH, './div[3]')
                    status_xpath = row.find_element(By.XPATH, './div[7]')
                    all_data.append(
                        {'item': item_xpath.text, 'status': status_xpath.text}
                    )
                except NoSuchElementException:
                    continue

            # Verificação para garantir que a rolagem esteja completa
            last_height = driver.execute_script(
                'return document.body.scrollHeight'
            )
            time.sleep(2)
            new_height = driver.execute_script(
                'return document.body.scrollHeight'
            )
            if new_height == last_height:
                break
    except NoSuchElementException as e:
        print(f'Erro ao encontrar o scrollbar: {e}')
    except TimeoutException as e:
        print(f'Tempo esgotado ao esperar pelo scrollbar: {e}')

    return all_data


# Função para coletar informações do site
def collect_info(driver):
    try:
        all_data = []
        for _ in range(3):
            all_data.extend(scroll_table_to_bottom(driver))

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

        return (
            count_success,
            count_business_error,
            count_system_failure,
            falha_detectada,
            tme_xpath,
            tef_xpath,
            backlog_xpath,
        )

    except WebDriverException as e:
        print(f'Erro ao coletar informações: {e}')
        return None, None, None, None, None, None, None


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


# Função para monitorar falhas e enviar mensagens de falha e recuperação
def monitor_falhas(driver):
    while True:
        (
            count_success,
            count_business_error,
            count_system_failure,
            falha_detectada,
            _,
            _,
            _,
        ) = collect_info(driver)

        if falha_detectada:
            send_telegram_message(
                'Falha de sistema\n\nℹ️ Informação: falha ao importar pedidos'
            )
            while falha_detectada:
                time.sleep(60)
                _, _, _, falha_detectada, _, _, _ = collect_info(driver)
            send_telegram_message(
                '✅ Robô retomado para produção - MVP1 ✅\n\n⏰ Status: operando normalmente'
            )

        time.sleep(60)  # Aguarda um minuto antes de verificar novamente


# Função para enviar mensagens informacionais
def send_informational_message(driver):
    (
        count_success,
        count_business_error,
        count_system_failure,
        _,
        tme_xpath,
        tef_xpath,
        backlog_xpath,
    ) = collect_info(driver)
    if count_success is not None:
        total_processos = (
            count_success + count_business_error + count_system_failure
        )
        if total_processos > 0:
            percent_success = (count_success / total_processos) * 100
            percent_business_error = (
                count_business_error / total_processos
            ) * 100
            percent_system_failure = (
                count_system_failure / total_processos
            ) * 100
        else:
            percent_success = (
                percent_business_error
            ) = percent_system_failure = 0

        message = (
            '🤖 *Automação PAP - MVP2*\n'
            f"{datetime.date.today().strftime('%d/%m/%Y')}\n\n"
            f'*Status do robô*: Operando ✅\n\n'
            f"📓*Informacional até {datetime.datetime.now().strftime('%Hh%M')}*\n"
            f'🗂*Backlog*: {backlog_xpath}\n'
            f'✅*Concluído com sucesso:* {count_success} ({percent_success:.2f}%)\n'
            f'⚠️*Erro de negócio:* {count_business_error} ({percent_business_error:.2f}%)\n'
            f'❌*Falha de sistema:* {count_system_failure} ({percent_system_failure:.2f}%)\n\n'
            f'⏱*Tempo médio de execução:* {tme_xpath}\n'
            f'⏱*Tempo de fila:* {tef_xpath}\n\n'
            f'🌐*Link para mais detalhes*: https://e-bots.co/grafana/goto/Fj3MALXIR?orgId=1 \n\n'
            f'🔰 Informacional desenv. - Projetos Tahto Aut/IA 🔰'
        )
        send_telegram_message(message)


# Função para agendar coletas regulares
def schedule_regular_collections(driver):
    schedule.every().monday.at('08:05').do(send_informational_message, driver)
    schedule.every().monday.at('12:05').do(send_informational_message, driver)
    schedule.every().monday.at('16:05').do(send_informational_message, driver)
    schedule.every().monday.at('20:05').do(send_informational_message, driver)

    schedule.every().tuesday.at('08:05').do(send_informational_message, driver)
    schedule.every().tuesday.at('12:05').do(send_informational_message, driver)
    schedule.every().tuesday.at('16:05').do(send_informational_message, driver)
    schedule.every().tuesday.at('20:05').do(send_informational_message, driver)

    schedule.every().wednesday.at('08:05').do(
        send_informational_message, driver
    )
    schedule.every().wednesday.at('14:38').do(
        send_informational_message, driver
    )
    schedule.every().wednesday.at('16:05').do(
        send_informational_message, driver
    )
    schedule.every().wednesday.at('20:05').do(
        send_informational_message, driver
    )

    schedule.every().thursday.at('08:05').do(
        send_informational_message, driver
    )
    schedule.every().thursday.at('12:05').do(
        send_informational_message, driver
    )
    schedule.every().thursday.at('16:05').do(
        send_informational_message, driver
    )
    schedule.every().thursday.at('20:05').do(
        send_informational_message, driver
    )

    schedule.every().friday.at('08:05').do(send_informational_message, driver)
    schedule.every().friday.at('12:05').do(send_informational_message, driver)
    schedule.every().friday.at('16:05').do(send_informational_message, driver)
    schedule.every().friday.at('20:05').do(send_informational_message, driver)

    schedule.every().saturday.at('09:05').do(
        send_informational_message, driver
    )
    schedule.every().saturday.at('12:05').do(
        send_informational_message, driver
    )
    schedule.every().saturday.at('15:55').do(
        send_informational_message, driver
    )


# Função principal
def main():
    driver = start_browser()
    authenticate(driver, email, password)

    # Rolar a página inteira e a tabela interna até o final após a autenticação
    scroll_to_bottom(driver)
    time.sleep(1)

    schedule_regular_collections(driver)

    # Iniciar monitoramento de falhas em uma thread separada
    falhas_thread = threading.Thread(target=monitor_falhas, args=(driver,))
    falhas_thread.daemon = True
    falhas_thread.start()

    while True:
        schedule.run_pending()
        time.sleep(1)


# Credenciais de login
email = 'guilherme.caseiro@tahto.com.br'
password = 'C453iro@102030.'

# Executa a função principal
if __name__ == '__main__':
    main()
