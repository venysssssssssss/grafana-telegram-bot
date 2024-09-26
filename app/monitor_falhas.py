import logging
import time
from threading import Thread

import schedule
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from send_telegram_msg import send_telegram_message


def collect_info(driver, dashboard_name):
    try:
        base_xpath = '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div'
        time.sleep(4)
        rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
        total_rows = len(rows)
        logging.info(
            f'{dashboard_name} - Total de linhas processadas: {total_rows}'
        )

        falha_detectada = False
        consecutive_failures = 0

        for row in range(1, min(4, total_rows + 1)):
            logging.info(f'{dashboard_name} - Linhas: {total_rows}')
            item_xpath = f'{base_xpath}[{row}]/div[3]'
            status_xpath = f'{base_xpath}[{row}]/div[7]'
            item = driver.find_element(By.XPATH, item_xpath).text
            status = driver.find_element(By.XPATH, status_xpath).text
            if (
                item == 'ValidarVendasLiberadas'
                and status == 'Falha de sistema'
            ):
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    falha_detectada = True
                    break
            else:
                consecutive_failures = 0
            logging.info(f'{dashboard_name} - Item: {item} - Status: {status}')

        return falha_detectada
    except WebDriverException as e:
        logging.error(f'Erro ao coletar informações: {e}')
        return False


def monitor_falhas(driver_mvp1, driver_mvp3):
    logging.info('Iniciando monitoramento de falhas para MVP1 e MVP3')

    def verificar_falhas(dashboard_name, driver):
        falha_detectada = collect_info(driver, dashboard_name)
        if falha_detectada:
            send_telegram_message(
                f'🤖 *{dashboard_name} - Falha de sistema* ❌\n\nℹ️ *Informação*: falha ao importar pedidos'
            )
            while falha_detectada:
                time.sleep(60)
                falha_detectada = collect_info(driver, dashboard_name)
            send_telegram_message(
                f'🤖 *{dashboard_name} - Em produção* ✅\n\n⏰ *Status*: operando normalmente'
            )

    # Verificar MVP1 e MVP3 a cada 2 minutos
    schedule.every(1).minutes.do(verificar_falhas, 'MVP1', driver_mvp1)
    schedule.every(1).minutes.do(verificar_falhas, 'MVP3', driver_mvp3)
    # schedule_regular_collections(driver, tme_xpath, tef_xpath, backlog_xpath, actions, browser_manager)

    # Iniciar o agendamento em uma thread separada
    scheduler_thread = Thread(target=run_scheduled_jobs)
    scheduler_thread.start()
    logging.info(
        'Thread de agendamento para monitoramento de MVP1 e MVP3 iniciada'
    )


def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)
