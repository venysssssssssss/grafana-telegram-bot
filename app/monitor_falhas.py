import time
from threading import Thread

import schedule
from schedule_regular import schedule_regular_collections
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from send_telegram_msg import send_telegram_message


def collect_info(driver):
    try:
        base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
        rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
        total_rows = len(rows)
        print(f'Total de linhas processadas: {total_rows}')

        falha_detectada = False
        for row in range(1, min(4, total_rows + 1)):
            item_xpath = f'{base_xpath}[{row}]/div[3]'
            status_xpath = f'{base_xpath}[{row}]/div[7]'
            item = driver.find_element(By.XPATH, item_xpath).text
            status = driver.find_element(By.XPATH, status_xpath).text
            if (
                item == 'ValidarVendasLiberadas'
                and status == 'Falha de sistema'
            ):
                falha_detectada = True
            print(f'Item: {item} - Status: {status}')
        return falha_detectada
    except WebDriverException as e:
        print(f'Erro ao coletar informações: {e}')
        return False

def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

def monitor_falhas(driver, tme_xpath, tef_xpath, backlog_xpath):
    schedule_regular_collections(driver, tme_xpath, tef_xpath, backlog_xpath)
    scheduler_thread = Thread(target=run_scheduled_jobs)
    scheduler_thread.start()
    # Loop de monitoramento de falhas
    while True:
        falha_detectada = collect_info(driver)
        if falha_detectada:
            send_telegram_message(
                'Falha de sistema\n\nℹ️ Informação: falha ao importar pedidos'
            )
            while falha_detectada:
                time.sleep(60)
                falha_detectada = collect_info(driver)
            send_telegram_message(
                '✅ Robô retomado para produção - MVP1 ✅\n\n⏰ Status: operando normalmente'
            )
        time.sleep(60)
