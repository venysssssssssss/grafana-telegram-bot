# Função para agendar coletas regulares
import schedule
from send_telegram_msg import send_informational_message

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
