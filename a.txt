import time
import logging
from threading import Thread
import schedule
from schedule_regular import schedule_regular_collections
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from send_telegram_msg import send_telegram_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def collect_info(driver):
    try:
        base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
        rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
        total_rows = len(rows)
        logger.info(f'Total de linhas processadas: {total_rows}')

        falha_count = 0
        for row in range(1, total_rows + 1):
            item_xpath = f'{base_xpath}[{row}]/div[3]'
            status_xpath = f'{base_xpath}[{row}]/div[7]'
            item = driver.find_element(By.XPATH, item_xpath).text
            status = driver.find_element(By.XPATH, status_xpath).text
            if item == 'ValidarVendasLiberadas' and status == 'Falha de sistema':
                falha_count += 1
            logger.info(f'Item: {item} - Status: {status}')

            # Se já tivermos 3 falhas, podemos parar de verificar
            if falha_count >= 3:
                return True

        return False
    except WebDriverException as e:
        logger.error(f'Erro ao coletar informações: {e}')
        return False

def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

def monitor_falhas(driver, tme_xpath, tef_xpath, backlog_xpath):
    logger.info("Iniciando monitoramento de falhas")
    schedule_regular_collections(driver, tme_xpath, tef_xpath, backlog_xpath)
    scheduler_thread = Thread(target=run_scheduled_jobs)
    scheduler_thread.start()
    logger.info("Thread de agendamento iniciada")

    # Loop de monitoramento de falhas
    falha_reportada = False
    while True:
        falha_detectada = collect_info(driver)
        if falha_detectada and not falha_reportada:
            send_telegram_message('🤖 *MVP1 - Falha de sistema* ❌\n\nℹ️ *Informação*: falha ao importar pedidos')
            falha_reportada = True
        elif not falha_detectada and falha_reportada:
            send_telegram_message('🤖 *MVP1 - Em produção* ✅\n\n⏰ *Status*: operando normalmente')
            falha_reportada = False
        time.sleep(60)
