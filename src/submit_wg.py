import logging
import time

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.firefox.service import Service

from openai import OpenAI

from src import ListingInfoGetter


def get_element(driver, by, id):
    remove_cookies_popup(driver)
    try:
        wait = WebDriverWait(driver, 10, poll_frequency=1)
        element = wait.until(EC.visibility_of_element_located((by, id)))
    except TimeoutException:
        wait = WebDriverWait(driver, 30, poll_frequency=1)
        element = wait.until(EC.presence_of_element_located((by, id)))
    if isinstance(element, list):
        element = element[0]
    return element


def click_button(driver, by, id):
    remove_cookies_popup(driver)
    try:
        element = get_element(driver, by, id)
        element.click()
    except ElementNotInteractableException:
        raise ElementNotInteractableException()


def click_at_coordinates(driver, x, y):
    remove_cookies_popup(driver)
    action = ActionChains(driver)
    action.move_by_offset(x, y).click().perform()


def remove_cookies_popup(driver):
    divs_to_remove = driver.find_elements(By.XPATH, "//div[@id='cmpbox' or @id='cmpbox2']")
    for div in divs_to_remove:
        driver.execute_script("arguments[0].remove();", div)


def send_keys(driver, by, id, send_str):
    try:
        element = get_element(driver, by, id)
        element.send_keys(send_str)
    except ElementNotInteractableException:
        raise ElementNotInteractableException(f"Could not enter: {send_str}")


def build_driver(config, logger):
    firefox_options = webdriver.FirefoxOptions()

    # add the argument to reuse an existing tab
    if config["run_headless"]:
        firefox_options.add_argument("--headless")

    if config["firefox_path"]:
        firefox_options.binary_location = config["firefox_path"]

    # create the Geckodriver object and log
    try:
        if config["geckodriver_path"] != "":
            driver = webdriver.Firefox(options=firefox_options, service=Service(config["geckodriver_path"]))
        else:
            driver = webdriver.Firefox(options=firefox_options)

        # mainly when using screen
        driver.maximize_window()
        driver.get("https://www.wg-gesucht.de/nachricht-senden" + config["ref"])

        return driver
    except Exception as e:
        logger.log(logging.ERROR, "Browser crashed! You might be trying to run it without a screen in terminal?")
        raise e


def submit_app(config, logger):
    driver = build_driver(config, logger)

    # remove cookie popup, as "Akzeptieren" doesn't show on headless Firefox on Linux for some reason
    remove_cookies_popup(driver)

    # click my account button
    click_button(driver, By.XPATH, "//*[contains(text(), 'Mein Konto')]")

    # enter email
    send_keys(driver, By.ID, "login_email_username", config["wg_gesucht_credentials"]["email"])

    # enter password
    send_keys(driver, By.ID, "login_password", config["wg_gesucht_credentials"]["password"])

    # click login button
    click_button(driver, By.ID, "login_submit")
    logger.info("Logged in.")

    # remove the occasional cookie popup again
    remove_cookies_popup(driver)

    # remove lightbox div that blocks attachments
    divs_to_remove = driver.find_elements(By.XPATH, "//div[@class='lightbox']")
    for div in divs_to_remove:
        driver.execute_script("arguments[0].remove();", div)

    # accept the occasional advice gives on how to stay safe
    try:
        click_button(driver, By.ID, "sicherheit_bestaetigung")
    except:
        pass

    # checks if a message has already been sent previously to listing
    try:
        _ = get_element(driver, By.ID, "message_timestamp")
        logger.info("Message has already been sent previously. Will skip this offer.")
        driver.quit()
        return False
    except:
        logger.info("No message has been sent. Will send now...")

    logger.info(f"Sending to: {config['user_name']}, {config['address']}.")

    text_area = get_element(driver, By.ID, "message_input")
    if text_area:
        text_area.clear()

    # read message from the file
    message_file = config["message_file"]
    try:
        with open(message_file, "r", encoding="utf-8") as file:
            message = str(file.read())
        message = message.replace("recipient", config["user_name"].split(" ")[0])

        # use GPT to check ads for "if you've read this write X"
        if config["openai_key"] != "":
            getter = ListingInfoGetter(config["ref"])
            text = getter.get_listing_text()

            client = OpenAI()
            completion = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                max_tokens=2000,
                prompt=
                f"""
                Du bist dabei, eine Nachricht auf WG-Gesucht an "{config['user_name']}" über ein Angebot mit folgender Beschreibung zu senden:

                "
                {text}
                "


                Deine Nachricht lautet:
                "
                {message}
                "


                Sorge dafür, dass die Nachricht entsprechend der Beschreibung angepasst ist. So wird in WG-Beschreibungen oft nach einer Antwort auf irgendeine Frage, oder auch nach dem Schreiben eines bestimmten Wortes gefragt.
                Zusätzlich muss die Nachricht ein wenig personalisiert werden durch kleine Anpassungen.

                Gib als Antwort nur die Nachricht an.
                """
            )

            message = completion.choices[0].text

        text_area.send_keys(message)
    except:
        logger.info(f"{message_file} file not found!")
        driver.quit()
        return False

    if config["attach_schufa"]:
        # open the attachment popup
        click_button(driver, By.CLASS_NAME, "btn.wgg_white.pull-right.mr10")

        # at the popup, open the file attachment selection
        click_button(driver, By.CLASS_NAME, "cursor-pointer.conversation-attachment-option.attach_file")

        # select (attach) the document named "SCHUFA-BonitaetsCheck.pdf"
        click_button(driver, By.XPATH, "//*[contains(text(), 'SCHUFA-BonitaetsCheck.pdf')]")

        # close attachment
        click_at_coordinates(driver, 100, 100)
        click_at_coordinates(driver, 100, 100)

    time.sleep(3)

    try:
        click_button(
            driver,
            By.XPATH,
            "//button[@data-ng-click='submit()' or contains(.,'Nachricht senden')]",
        )
        logger.info(f">>>> Message sent to: {config['ref']} <<<<")
        time.sleep(2)
        driver.quit()
        return True
    except ElementNotInteractableException:
        logger.info("Cannot find submit button!")
        driver.quit()
        return False
