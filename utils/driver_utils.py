import undetected_chromedriver as uc

def get_driver(headless=False):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")

    prefs = {"intl.accept_languages": "en,en_US"}
    options.add_experimental_option("prefs", prefs)

    if headless:
        options.headless = True

    driver = uc.Chrome(options=options, version_main=138)
    return driver

