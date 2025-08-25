from selenium.webdriver.common.by import By
from utils.selenium_utils import SeleniumHelper
from TextMagic.notifier import TextMagicNotifier
from utils.driver_utils import get_driver  
from utils.notification_utils import load_recipients_from_file
from utils.logger import setup_logger
from lxml import html
import re
import time
import os

class BookingAutomationBot: 
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.driver = get_driver(headless=False)
        self.helper = SeleniumHelper(self.driver)
        self.notifier = TextMagicNotifier(config)
        base_dir = os.path.dirname(os.path.dirname(__file__)) 
        recipients_file = os.path.join(base_dir, "config", "recipients.txt")
        self.recipients = load_recipients_from_file(recipients_file)
        if not self.recipients:
            self.logger.warning("Recipient list is empty. No messages will be sent.")

    def run(self):
        self.logger.info("Launching browser and navigating to login page...")
        time.sleep(2)
        self.driver.maximize_window()
        self.driver.get(self.config["LOGIN_URL"])
        time.sleep(5)

        try:
            self.helper.scroll_into_view(By.XPATH, '//p[normalize-space(text()) = "This service is available from 6am to midnight."]')
            self.helper.wait_and_click(By.XPATH, '//span[normalize-space(text()) = "Start now"]//parent::a')
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"Error in Clicking 'Start now' button: {e}")
               
        # Step 1: CAPTCHA
        if self.detect_captcha():
            self.send_message_to_all("CAPTCHA detected. Please complete it to continue.")
            self.logger.info("Waiting for user to complete CAPTCHA...")
            if self.helper.wait_for_input("Have you completed the CAPTCHA? (yes/no): ", "yes"):
                print("Thank you! Proceeding with the rest of the code...")

        # Access Denied here means full exit
        access_denied_status = self.check_for_access_denied_and_restart(allow_restart=False)
        if access_denied_status == "EXIT":
            return False

        # Step 2: Login Screen
        if self.on_login_screen():
            self.login()
    
        # Step 3: Booking Form
        self.logger.info("Filling out the booking form...")
        self.fill_booking_form()

        # Step 4: Find a Green Slot
        self.logger.info("Scanning for available (green) test slots...") 
        result = self.find_green_slot()
        
        if result == ("RESTART", None):
            return True  # Signal main() to restart

        found, available_slots = result
        if found:
            message = f"Found the ({available_slots}) green slot(s). Please jump on the PC and complete the booking."
            self.send_message_to_all(message)
            self.logger.info("Green slot found and notified.")
            self.helper.capture_screenshot("green_slot_found.png")
        else:
            self.logger.info("No green slot found.")

        self.driver.quit()
        return False

    # -----------------------
    # Individual Task Methods
    # -----------------------

    def send_message_to_all(self, message):
        for number in self.recipients:
            try:
                self.notifier.send_message(number, message)
                self.logger.info(f"Message sent to {number}")
            except Exception as e:
                self.logger.error(f"Failed to send message to {number}: {e}")

    def detect_captcha(self):
        try:
            self.logger.info("Checking for CAPTCHA...")
            self.logger.info("Switching iframe.")
            iframe = self.driver.find_element(By.XPATH, '//iframe[@id="main-iframe"]')
            self.driver.switch_to.frame(iframe)
            if self.driver.find_element(By.XPATH, "//p[normalize-space(.) = 'Additional security check is required']"):
                self.logger.info("Exiting iframe.")
                self.driver.switch_to.default_content()
                return True
        except:
            return False
        
    def on_login_screen(self):
        try:
            self.logger.info("Checking for Login Screen...")
            self.helper.scroll_into_view(By.XPATH, "//h1[normalize-space(.) = 'Sign in using Government Gateway']")
            return self.driver.find_element(By.XPATH, "//label[normalize-space(text()) = 'Government Gateway user ID']").is_displayed()
        except:
            return False

    def login(self):
        try:
            self.logger.info("Attempting to log in with credentials from config...")
            self.send_message_to_all("Login screen detected. Automatically logging in...")

            # Find and fill user ID
            user_input = self.driver.find_element(By.XPATH, '//input[@name="user_id"]')
            user_input.clear()
            user_input.send_keys(self.config["USERNAME"])
            self.logger.debug("Entered username.")

            # Find and fill password
            password_input = self.driver.find_element(By.XPATH, '//input[@name="password"]')
            password_input.clear()
            password_input.send_keys(self.config["PASSWORD"])
            self.logger.debug("Entered password.")

            # Click the Sign In button
            self.helper.wait_and_click(By.XPATH, "//button[normalize-space(text())='Sign in']")
            self.logger.info("Login form submitted.")
            time.sleep(3)  

        except Exception as e:
            self.logger.error(f"Error during login automation: {e}")
            self.helper.capture_screenshot("login_error.png")
            self.send_message_to_all("Login automation failed. Please complete it manually.")
            raise RuntimeError("Automated login failed.")

    def fill_booking_form(self):
        try:
            self.helper.scroll_into_view(By.XPATH, "//legend[normalize-space(text()) = 'Find available tests']")

            # to select booking Category from its dropdown
            self.helper.select_dropdown_by_value(By.XPATH, "//label[normalize-space(.) = 'Please choose business booking test category']//parent::div//select[@class='select']",
                                                 self.config["CATEGORY"])

            # to select booking Center from its dropdown
            self.helper.select_dropdown_by_value(By.XPATH, "(//label[normalize-space()='Favourite test centre group (optional)']//ancestor::div)[5]//select",
                                                 self.config["BOOKING_CENTER"])

            # to select special needs or disabilities button
            self.helper.select_radio_option_if_available(By.XPATH, "//span[normalize-space()='Does the candidate have any special needs or disabilities?']", 
                                                         f"(//span[normalize-space()='Does the candidate have any special needs or disabilities?']//ancestor::div[@class='clearfix'])[2]//input[@value='{self.config['DISABILITY']}']")

            self.helper.wait_and_click(By.XPATH, "//input[normalize-space(@value)='Book test']")
            self.logger.info("Booking form submitted.")
        except Exception as e:
            self.logger.error(f"Error filling booking form: {e}")
            self.helper.capture_screenshot("booking_form_error.png")

    def check_all_slots(self):
        for slot_number in range(1, 36):
            slot_xpath = f"(//td[contains(@class, 'day')]//a)[{slot_number}]"
            try:
                slot_element = self.driver.find_element(By.XPATH, slot_xpath)
                slot_html = slot_element.get_attribute("outerHTML")
                background_color = slot_element.value_of_css_property("background-color").strip()

                parsed_html = html.fromstring(slot_html)
                anchor_tags = parsed_html.xpath("//a")

                if anchor_tags:
                    visible_text = ''.join(anchor_tags[0].itertext()).strip()
                    number_match = re.search(r'\b\d+\b', visible_text)
                    available_slots = int(number_match.group()) if number_match else 0
                else:
                    available_slots = 0

                self.logger.info(f"Slot {slot_number} Value: {available_slots} and Color: {background_color}")
                GREEN_COLORS = ["rgb(0, 119, 0)", "rgba(0, 119, 0, 1)"]
                if background_color in GREEN_COLORS or available_slots > 0:
                    self.logger.info(f"✅ Green slot found at position {slot_number}! Clicking...")
                    slot_element.click()
                    return True, available_slots

            except Exception as e:
                self.logger.warning(f"Slot {slot_number} not found or caused error: {e}")
                continue
        return False, None

    def check_for_access_denied_and_restart(self, allow_restart=True):
        try:
            self.logger.debug("Checking for 'Access Denied Error 15' dialog...")
            try:
                access_denied_elem = self.driver.find_element(By.XPATH, '//div[@role="dialog"]')
            except:
                self.logger.info("Switching iframe.")
                iframe = self.driver.find_element(By.XPATH, '//iframe[@id="main-iframe"]')
                self.driver.switch_to.frame(iframe)
                try: 
                    access_denied_elem = self.driver.find_element(By.XPATH, '//div[text()="Access Denied"]')
                except: 
                    access_denied_elem = self.driver.find_element(By.XPATH, '//div[text()="Error 15"]')
  
            if access_denied_elem.is_displayed():
                self.driver.switch_to.default_content()
                self.logger.error("Access Denied (Error 15) detected.")
                self.helper.capture_screenshot("access_denied_error_15.png")
                self.send_message_to_all("Access Denied (Error 15) detected.")
                self.driver.quit()
                if allow_restart:
                    return "RESTART"
                else:
                    return "EXIT"
        except:
            pass
        return None
    
    def find_green_slot(self):
        try:
            self.helper.scroll_into_view(By.XPATH, "//a[normalize-space(text()) = 'next available']")
            while True:  # Continue indefinitely until a green slot is found
                # FORWARD: Check across 10 weeks
                for week in range(10):
                    if self.check_for_access_denied_and_restart(allow_restart=True) == "RESTART":
                        return "RESTART", None

                    found, available_slots = self.check_all_slots()
                    if found:
                        return True, available_slots

                    if self.check_for_access_denied_and_restart(allow_restart=True) == "RESTART":
                        return "RESTART", None

                    try:
                        self.helper.wait_and_click(By.XPATH, "//a[normalize-space(text()) = 'next week']")
                        self.logger.info(f"Moving forward to week {week + 2}...")
                        time.sleep(0.5)
                    except Exception as e:
                        self.logger.warning(f"Could not click 'next week': {e}")
                        break  # Break the forward loop if navigation fails

                # BACKWARD: Return week by week (10 steps back)                
                for back_week in range(10):
                    if self.check_for_access_denied_and_restart(allow_restart=True) == "RESTART":
                        return "RESTART", None

                    try:
                        self.helper.wait_and_click(By.XPATH, "//a[normalize-space(text()) = 'previous week']")
                        self.logger.info(f"Moving back to week {8 - back_week - 1}...")
                        time.sleep(0.5)

                        if self.check_for_access_denied_and_restart(allow_restart=True) == "RESTART":
                            return "RESTART", None

                        found, available_slots = self.check_all_slots()
                        if found:
                            return True, available_slots
                    except Exception as e:
                        self.logger.warning(f"Could not click 'previous week': {e}")
                        break  # Break the backward loop if navigation fails

        except Exception as e:
            self.logger.error(f"Error during green slot search: {e}")
            self.helper.capture_screenshot("green_slot_search_error.png")
            return False, None
