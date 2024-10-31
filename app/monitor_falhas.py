import logging
import time
from queue import Queue
from threading import Event, Lock, Thread

import schedule
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from app.authentication import Authenticator
from app.send_telegram_msg import send_telegram_message

# Evento para controlar pausa e retomada do monitoramento
monitor_event = Event()
monitor_event.set()  # Iniciado como "ativo"

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def iniciar_monitoramento():
    """Retoma o monitoramento de falhas."""
    if not monitor_event.is_set():
        logging.info('Iniciando monitoramento de falhas...')
        monitor_event.set()


def pausar_monitoramento():
    """Pausa o monitoramento de falhas."""
    if monitor_event.is_set():
        logging.info('Pausando monitoramento de falhas...')
        monitor_event.clear()


def realizar_login(driver, url_mvp1):
    """Realiza login no dashboard MVP1."""
    try:
        logging.info(f'Realizando login no MVP1: {url_mvp1}')
        driver.get(url_mvp1)
        auth = Authenticator(driver)
        auth.authenticate()
        logging.info('Login no MVP1 concluído com sucesso.')
    except WebDriverException as e:
        logging.error(f'Erro ao realizar login no MVP1: {e}')


def collect_info(driver, dashboard_name, dashboard_url):
    """Coleta informações do dashboard e verifica falhas."""
    if not monitor_event.is_set():
        logging.info(
            f'Monitoramento pausado, não verificando {dashboard_name}'
        )
        return False

    try:
        logging.info(f'Acessando URL para {dashboard_name}: {dashboard_url}')
        driver.get(dashboard_url)
        time.sleep(5)

        base_xpath = (
            '/html/body/div[1]/div[1]/div/main/div/div/div[3]/div/div[1]/div/div/'
            'div[1]/div/div/div[8]/div/div/div[3]/div/div/div[1]/div/div[2]/div/'
            'div[1]/div/div/div'
        )
        rows = driver.find_elements(By.XPATH, f'{base_xpath}/div[3]')
        total_rows = len(rows)
        logging.info(f'Total de linhas: {total_rows}')

        consecutive_failures = 0
        falha_detectada = False

        for row in range(1, min(4, total_rows + 1)):
            item_xpath = f'{base_xpath}[{row}]/div[3]'
            status_xpath = f'{base_xpath}[{row}]/div[7]'
            item = driver.find_element(By.XPATH, item_xpath).text
            status = driver.find_element(By.XPATH, status_xpath).text

            logging.info(f'Item: {item} - Status: {status}')
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

        return falha_detectada
    except WebDriverException as e:
        logging.error(f'Erro ao coletar informações: {e}')
        return False


def monitor_falhas(
    driver_mvp1, driver_mvp3, url_mvp1, url_mvp3, lock, task_queue
):
    """Inicia o monitoramento de falhas nos dashboards."""
    logging.info('Iniciando monitoramento de falhas para MVP1 e MVP3')

    def verificar_falhas(dashboard_name, driver, url):
        """Função interna para verificar falhas."""
        with lock:
            if not task_queue.empty():
                logging.info('Tarefa em andamento, adiando verificação.')
                return

            if not monitor_event.is_set():
                logging.info(
                    f'Monitoramento pausado, adiando verificação em {dashboard_name}.'
                )
                return

            falha_detectada = collect_info(driver, dashboard_name, url)
            if falha_detectada:
                send_telegram_message(
                    f'🤖 *{dashboard_name} - Falha de sistema* ❌\n\n'
                    f'ℹ️ *Informação*: falha ao importar pedidos'
                )
                while (
                    falha_detectada and monitor_event.is_set()
                ):  # Verifica o status de execução
                    time.sleep(60)
                    falha_detectada = collect_info(driver, dashboard_name, url)
                if (
                    monitor_event.is_set()
                ):  # Envia mensagem se o monitoramento estiver ativo
                    send_telegram_message(
                        f'🤖 *{dashboard_name} - Em produção* ✅\n\n'
                        f'⏰ *Status*: operando normalmente'
                    )

    # Realizar login no MVP1 antes de iniciar o monitoramento
    realizar_login(driver_mvp1, url_mvp1)

    # Agendamento periódico para verificar falhas
    schedule.every(1).minutes.do(
        verificar_falhas, 'MVP1', driver_mvp1, url_mvp1
    )
    schedule.every(1).minutes.do(
        verificar_falhas, 'MVP3', driver_mvp3, url_mvp3
    )

    # Loop de monitoramento em uma thread separada
    while True:
        if monitor_event.is_set():
            schedule.run_pending()
        time.sleep(5)
