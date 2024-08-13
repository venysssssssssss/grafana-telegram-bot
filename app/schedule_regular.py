import schedule
import logging
from execute_download_actions import execute_download_actions
from send_telegram_msg import send_informational_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def download_and_send_message(actions, browser_manager, tme_xpath, tef_xpath, backlog_xpath):
    download_path = browser_manager.clean_download_directory('data')
    relatorio_path = execute_download_actions(actions, browser_manager, download_path)
    send_informational_message(browser_manager.driver, tme_xpath, tef_xpath, backlog_xpath, relatorio_path)

def schedule_for_day(day, times, func, *args):
    for time in times:
        logger.info(f"Agendando tarefa para {day} às {time}")
        getattr(schedule.every(), day).at(time).do(func, *args)

def schedule_regular_collections(driver, tme_xpath, tef_xpath, backlog_xpath, actions, browser_manager):
    schedule_dict = {
        'monday': ['08:05', '12:05', '16:05', '20:05'],
        'tuesday': ['08:05', '12:05','15:14', '16:05', '20:05'],
        'wednesday': ['08:05', '10:45', '13:01', '14:54', '16:05', '20:05'],
        'thursday': ['08:05', '12:05', '16:05', '20:05', '14:30', '15:30'],
        'friday': ['08:05', '12:05', '16:05', '20:05'],
        'saturday': ['09:05', '12:05', '15:55'],
    }
    for day, times in schedule_dict.items():
        for time in times:
            logger.info(f"Agendando tarefa para {day} às {time}")
            schedule.every().day.at(time).do(download_and_send_message, actions, browser_manager, tme_xpath, tef_xpath, backlog_xpath)
    logger.info("Tarefas de agendamento configuradas")
