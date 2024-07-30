from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ActionManager:
    def __init__(self, driver):
        self.driver = driver
        self.action = ActionChains(driver)

    def move_to_and_interact(self, xpath, keys=None):
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        self.action.move_to_element(element).perform()
        if keys:
            self.action.send_keys(keys).perform()
        time.sleep(2)  # Adjust according to the response time of the webpage

    def click_element(self, xpath):
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        self.action.click(element).perform()
        time.sleep(0.5)  # Short sleep to ensure the action is registered

