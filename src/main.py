import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import requests
import datetime
import schedule
import threading

# Função para iniciar o navegador Edge em modo headless
def start_browser():
    service = Service('msedgedriver.exe')  # Substitua pelo caminho correto do EdgeDriver
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(service=service, options=options)
    return driver

# Função para autenticar no site
def authenticate(driver, email, password):
    login_url = 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&var-Robot=tahto-pap-mvp2&var-Robot_id=82&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now&refresh=30s'
    driver.get(login_url)
    time.sleep(5)
    
    try:
        email_element = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[1]/div[2]/div/div/div/input')
        password_element = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/div[2]/div[2]/div/div/div/input')
        
        email_element.send_keys(email)
        password_element.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div/div[3]/div/div/div[2]/div/div/form/button')
        login_button.click()
        
        # Aguarda o login ser processado e a nova página carregar
        time.sleep(5)
    except NoSuchElementException as e:
        print(f"Erro ao encontrar elementos de login: {e}")
        driver.quit()

# Função para enviar mensagem via Telegram
def send_telegram_message(message):
    telegram_token = '7226155746:AAEBPeOtzJrD_KQyeZinNBjh5HMmvHTBZLs'  # Substitua pelo token do seu bot do Telegram
    chat_id = '-1002165188451'  # Substitua pelo seu chat ID
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

# Função para rolar a tabela até o final
def scroll_table(driver, base_xpath, row):
    if row % 15 == 0:
        try:
            scroll_element = driver.find_element(By.XPATH, '//div[@class="track-vertical"]/div[@class="thumb-vertical"]')
            driver.execute_script("arguments[0].style.transform = 'translateY({}px)';".format(row * 10), scroll_element)
            time.sleep(1)  # Aguarda a tabela carregar novas linhas
        except NoSuchElementException as e:
            print(f"Erro ao rolar a tabela: {e}")

# Função para coletar informações do site
def collect_info(driver):
    try:
        # XPATH base para as linhas da tabela
        base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
        count_success = 0
        count_business_error = 0
        count_system_failure = 0
        falha_detectada = False

        # Coleta os valores dos XPaths adicionais
        tme_xpath = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[5]/div/div/div[3]/div/div/div/div/div/div/span").text
        tef_xpath = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[6]/div/div/div[3]/div/div/div/div/div/div/span").text
        backlog_xpath = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div/div[3]/div/div/div/div/div/div/span").text

        # Encontrar o número total de linhas na tabela
        rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
        total_rows = len(rows)

        print(f"Total de linhas processadas: {total_rows}")

        # Verificar todas as linhas da tabela
        for row in range(1, total_rows + 1):
            try: 
                item_xpath = f'{base_xpath}[{row}]/div[3]'
                status_xpath = f'{base_xpath}[{row}]/div[7]'
                
                item = driver.find_element(By.XPATH, item_xpath).text
                status = driver.find_element(By.XPATH, status_xpath).text

                if row <= 3:
                    if item == "ValidarVendasLiberadas" and status == "Falha de sistema":
                        falha_detectada = True
                    else:
                        falha_detectada = False

                if status == "Concluído com sucesso" and item != "ValidarVendasLiberadas":
                    count_success += 1
                elif status == "Erro de negócio" and item != "ValidarVendasLiberadas":
                    count_business_error += 1
                elif status == "Falha de sistema" and item != "ValidarVendasLiberadas":
                    count_system_failure += 1

                scroll_table(driver, base_xpath, row)  # Rola a cada 15 linhas
            except NoSuchElementException:
                break

        return count_success, count_business_error, count_system_failure, falha_detectada, tme_xpath, tef_xpath, backlog_xpath

    except WebDriverException as e:
        print(f"Erro ao coletar informações: {e}")
        return None, None, None, None, None, None, None

# Função para monitorar falhas e enviar mensagens de falha e recuperação
def monitor_falhas(driver):
    while True:
        count_success, count_business_error, count_system_failure, falha_detectada, _, _, _ = collect_info(driver)
        
        if falha_detectada:
            send_telegram_message("Falha de sistema\n\nℹ️ Informação: falha ao importar pedidos")
            while falha_detectada:
                time.sleep(60)
                _, _, _, falha_detectada, _, _, _ = collect_info(driver)
            send_telegram_message("✅ Robô retomado para produção - MVP1 ✅\n\n⏰ Status: operando normalmente")
        
        time.sleep(60)  # Aguarda um minuto antes de verificar novamente

# Função para enviar mensagens informacionais
def send_informational_message(driver):
    count_success, count_business_error, count_system_failure, _, tme_xpath, tef_xpath, backlog_xpath = collect_info(driver)
    if count_success is not None:
        total_processos = count_success + count_business_error + count_system_failure
        if total_processos > 0:
            percent_success = (count_success / total_processos) * 100
            percent_business_error = (count_business_error / total_processos) * 100
            percent_system_failure = (count_system_failure / total_processos) * 100
        else:
            percent_success = percent_business_error = percent_system_failure = 0
        
        message = ("🤖 *Automação PAP - MVP1*\n"
                   f"{datetime.date.today().strftime('%d/%m/%Y')}\n\n"
                   f"*Status do robô*: Operando ✅\n\n"
                   f"📓*Informacional até {datetime.datetime.now().strftime('%Hh%M')}*\n"
                   f"🗂*Backlog*: {backlog_xpath}\n"
                   f"✅*Concluído com sucesso:* {count_success} ({percent_success:.2f}%)\n"
                   f"⚠️*Erro de negócio:* {count_business_error} ({percent_business_error:.2f}%)\n"
                   f"❌*Falha de sistema:* {count_system_failure} ({percent_system_failure:.2f}%)\n\n"
                   f"⏱*Tempo médio de execução:* {tme_xpath}\n"
                   f"⏱*Tempo de fila:* {tef_xpath}\n\n"
                   f"🌐*Link para mais detalhes*: https://e-bots.co/grafana/goto/Fj3MALXIR?orgId=1 \n\n"
                   f"🔰 Informacional desenv. - Projetos Tahto Aut/IA 🔰")
        send_telegram_message(message)

# Função para agendar coletas regulares
def schedule_regular_collections(driver):
    schedule.every().monday.at("08:05").do(send_informational_message, driver)
    schedule.every().monday.at("12:05").do(send_informational_message, driver)
    schedule.every().monday.at("16:05").do(send_informational_message, driver)
    schedule.every().monday.at("20:05").do(send_informational_message, driver)

    schedule.every().tuesday.at("08:05").do(send_informational_message, driver)
    schedule.every().tuesday.at("12:05").do(send_informational_message, driver)
    schedule.every().tuesday.at("16:05").do(send_informational_message, driver)
    schedule.every().tuesday.at("20:05").do(send_informational_message, driver)

    schedule.every().wednesday.at("08:05").do(send_informational_message, driver)
    schedule.every().wednesday.at("14:38").do(send_informational_message, driver)
    schedule.every().wednesday.at("16:05").do(send_informational_message, driver)
    schedule.every().wednesday.at("20:05").do(send_informational_message, driver)

    schedule.every().thursday.at("08:05").do(send_informational_message, driver)
    schedule.every().thursday.at("12:05").do(send_informational_message, driver)
    schedule.every().thursday.at("16:05").do(send_informational_message, driver)
    schedule.every().thursday.at("20:05").do(send_informational_message, driver)

    schedule.every().friday.at("08:05").do(send_informational_message, driver)
    schedule.every().friday.at("12:05").do(send_informational_message, driver)
    schedule.every().friday.at("16:05").do(send_informational_message, driver)
    schedule.every().friday.at("20:05").do(send_informational_message, driver)

    schedule.every().saturday.at("09:05").do(send_informational_message, driver)
    schedule.every().saturday.at("12:05").do(send_informational_message, driver)
    schedule.every().saturday.at("15:55").do(send_informational_message, driver)

# Função principal
def main():
    driver = start_browser()
    authenticate(driver, email, password)
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
if __name__ == "__main__":
    main()
