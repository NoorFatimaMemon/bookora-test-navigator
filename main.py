from bot.automation_engine import BookingAutomationBot
from utils.config_loader import ConfigLoader
import time

def main():
    config = ConfigLoader.load()
    while True:
        bot = BookingAutomationBot(config)
        time.sleep(2)
        should_restart = bot.run()
        if should_restart: 
            print("Restarting bot due to Access Denied (Error 15)...")
            time.sleep(5)
        else:
            break

if __name__ == "__main__":
    main()
