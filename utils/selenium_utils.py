from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import os

class SeleniumHelper:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locatorType, locator, timeout=15):
        try: 
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((locatorType, locator)))
        except TimeoutException:
            return None

    def wait_and_click(self, locatorType, locator, timeout=15):
        try:
            element = self.wait_for_element(locatorType, locator, timeout)
            element.click()
        except TimeoutException:
            return False
        return True

    def get_element_text(self, locatorType, locator):
        try:
            element = self.driver.find_element(locatorType, locator)
            return element.text if element else None
        except Exception as e:
            return None
    
    def select_dropdown_by_value(self, locatorType, locator, value, timeout=15):
        dropdown = self.wait_for_element(locatorType, locator, timeout)
        if dropdown:
            ActionChains(self.driver).move_to_element(dropdown).click_and_hold().perform()
            option_xpath = f"{locator}//option[normalize-space(.) = '{value}']"
            option = self.wait_for_element(locatorType, option_xpath, timeout)
            if option:
                option.click()
            ActionChains(self.driver).release().perform()

    def select_radio_option_if_available(self, locatorType, container_xpath, option_xpath, timeout=15):
        container = self.wait_for_element(locatorType, container_xpath, timeout)
        if container:
            option = self.wait_for_element(locatorType, option_xpath, timeout)
            if option:
                option.click()

    def scroll_into_view(self, locatorType, locator):
        try:
            element = self.driver.find_element(locatorType, locator)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            return element
        except NoSuchElementException:
            return None

    def wait_for_input(self, prompt_message, expected_response):
        while True:
            user_input = input(prompt_message)
            if user_input.strip().lower() == expected_response.strip().lower():
                return True
            else:
                print(f"Please respond with '{expected_response}' to continue.")
    
    def capture_screenshot(self, label="screenshot"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = f"screenshots/{label}_{timestamp}.png"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.driver.save_screenshot(path)
        return path

    def save_html_dump(self, label="error_page"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = f"html_dumps/{label}_{timestamp}.html"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        return path
