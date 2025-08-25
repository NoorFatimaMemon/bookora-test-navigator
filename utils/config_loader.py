import os
from dotenv import load_dotenv
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load(env_file=".env"):
        """Loads environment variables from the config/.env file."""
        env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
        load_dotenv(dotenv_path=env_path, override=True)  

        return {
            # Login / URL
            "LOGIN_URL": os.getenv("LOGIN_URL"),
            "USERNAME": os.getenv("USERNAME"),
            "PASSWORD": os.getenv("PASSWORD"),

            # Booking Preferences
            "BOOKING_CENTER": os.getenv("BOOKING_CENTER", "Test Center 1"),
            "CATEGORY": os.getenv("CATEGORY", "Car"),
            "DISABILITY": os.getenv("DISABILITY", "No"),

            # TEXTMAGIC
            "TEXTMAGIC_USERNAME": os.getenv("TEXTMAGIC_USERNAME"),
            "TEXTMAGIC_API_KEY": os.getenv("TEXTMAGIC_API_KEY"),
        }
