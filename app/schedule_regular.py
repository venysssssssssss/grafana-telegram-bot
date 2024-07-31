import schedule
from send_telegram_msg import send_informational_message

def schedule_for_day(day, times, func, *args):
    for time in times:
        getattr(schedule.every(), day).at(time).do(func, *args)

def schedule_regular_collections(driver, tme_xpath, tef_xpath, backlog_xpath):
    schedule_dict = {
        'monday': ['08:05', '12:05', '16:05', '20:05'],
        'tuesday': ['08:05', '12:05', '16:05', '20:05'],
        'wednesday': ['08:05', '10:45', '12:50', '14:38', '16:05', '20:05'],
        'thursday': ['08:05', '12:05', '16:05', '20:05'],
        'friday': ['08:05', '12:05', '16:05', '20:05'],
        'saturday': ['09:05', '12:05', '15:55'],
    }
    for day, times in schedule_dict.items():
        schedule_for_day(day, times, send_informational_message, driver, tme_xpath, tef_xpath, backlog_xpath)
