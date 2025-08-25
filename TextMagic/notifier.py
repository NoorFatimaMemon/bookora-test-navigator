import requests
from utils.logger import setup_logger
from requests.auth import HTTPBasicAuth

class TextMagicNotifier:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()

    def send_message(self, to_phone, message):
        url = "https://rest.textmagic.com/api/v2/messages"
        payload = {"text": message,"phones": to_phone}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers,json=payload, 
                                     auth=HTTPBasicAuth(self.config["TEXTMAGIC_USERNAME"], 
                                                        self.config["TEXTMAGIC_API_KEY"]))
            response.raise_for_status()
            self.logger.info(f"Message '{message}' sent successfully!")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error: {http_err}")
            self.logger.error("Response:", response.text)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
