<<<<<<< HEAD
import logging
=======
# -*- coding: utf-8 -*-
import json
>>>>>>> upstream/main
import time
import re
from playwright.sync_api import sync_playwright, Page
from openai import OpenAI
from src import ListingInfoGetter

<<<<<<< HEAD
def remove_cookies_popup(page: Page):
=======
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src import OpenAIHelper


def get_element(driver, by, id):
    ignored_exceptions = (
        StaleElementReferenceException,
        NoSuchElementException,
        ElementNotInteractableException,
    )
    remove_cookies_popup(driver)
>>>>>>> upstream/main
    try:
        # More aggressive removal of various cookie consent IDs and classes
        # Added #sec_advice which is the "security advice" modal intercepting clicks
        page.evaluate("""() => {
            const selectors = ['#cmpbox', '#cmpbox2', '.cmpboxBG', '#cmpv6container', '.qc-cmp2-container', '#sec_advice', '.modal-backdrop'];
            selectors.forEach(s => {
                document.querySelectorAll(s).forEach(el => el.remove());
            });
            // Also enable scrolling if it was disabled by the popup
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        }""")
    except:
        pass

<<<<<<< HEAD
def remove_lightbox(page: Page):
=======

def click_button(driver, by, id):
    remove_cookies_popup(driver)
    driver.implicitly_wait(2)
>>>>>>> upstream/main
    try:
        page.evaluate("() => { document.querySelectorAll('.lightbox, .modal-backdrop, .modal-open').forEach(el => el.remove()); }")
    except:
        pass

<<<<<<< HEAD
def build_context(p, config, logger):
    # Use Firefox as requested for the "Firefox only" project
    browser = p.firefox.launch(headless=config.get("run_headless", True))
    context = browser.new_context()
    
    # Add a script to remove banners and modals as soon as they appear
    context.add_init_script("""
        setInterval(() => {
            ['#cmpbox', '#cmpbox2', '.cmpboxBG', '#cmpv6container', '.qc-cmp2-container', '#sec_advice', '.modal-backdrop'].forEach(s => {
                document.querySelectorAll(s).forEach(el => el.remove());
            });
            // Ensure document is clickable
            if (document.body.classList.contains('modal-open')) {
                document.body.classList.remove('modal-open');
                document.body.style.overflow = 'auto';
            }
        }, 500);
    """)
    
    page = context.new_page()
    
    # Standard WG-Gesucht window size
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    try:
        page.goto("https://www.wg-gesucht.de/nachricht-senden" + config["ref"], timeout=60000)
        return browser, page
    except Exception as e:
        logger.error("Browser failed to load page!")
        browser.close()
        raise e
=======

def click_at_coordinates(driver, x, y):
    remove_cookies_popup(driver)
    driver.implicitly_wait(2)
    action = ActionChains(driver)
    action.move_by_offset(x, y).click().perform()


def remove_cookies_popup(driver):
    divs_to_remove = driver.find_elements(
        By.XPATH, "//div[@id='cmpbox' or @id='cmpbox2']"
    )
    for div in divs_to_remove:
        driver.execute_script("arguments[0].remove();", div)


def send_keys(driver, by, id, send_str):
    driver.implicitly_wait(2)
    try:
        element = get_element(driver, by, id)
        element.send_keys(send_str)
    except ElementNotInteractableException:
        raise ElementNotInteractableException(f"Could not enter: {send_str}")


def gpt_get_language(config, logger) -> str:
    openai = OpenAIHelper(config["openai_credentials"]["api_key"])
    listing_text = config["listing_text"]

    if len(listing_text) < 200:
        listing_text = listing_text[10:]
    else:
        listing_text = listing_text[10:200]

    # build prompt
    prompt_lst = []
    prompt_lst.append("What language is this:\n")
    prompt_lst.append(listing_text)
    prompt_lst.append(" Please only respond in a JSON style format like ")
    prompt_lst.append('{"language": "<your-answer>"}, '),
    prompt_lst.append(
        "where your answer should be a single word which is the language."
    )
    prompt = "".join(prompt_lst)

    # pass prompt into openai helper method
    response = str(openai.generate(prompt)).strip()
    # response = '{"language": "German"}'
    logger.info(f"GPT response: {response}")

    # try to load json from string
    try:
        response_json = json.loads(response)
    except ValueError:
        logger.info("Response was not valid JSON format.")
        return ""
    return response_json.get("language", "")


def gpt_get_keyword(config, logger) -> str:
    openai = OpenAIHelper(config["openai_credentials"]["api_key"])
    listing_text = config["listing_text"]

    prompt_lst = []
    prompt_lst.append(
        "Check if there exists a keyword in the text, to show I read the text.\n"
    )
    prompt_lst.append(
        'This keyword is most likely wrapped in quotation marks like: "".\n'
    )
    prompt_lst.append(
        "Note however that not all texts will include such a keyword. Here is the text:\n"
    )
    prompt_lst.append(f"'{listing_text}'")
    prompt_lst.append("\nPlease only respond in JSON format like ")
    prompt_lst.append('{"keyword": "<your-keyword>"}, ')
    prompt_lst.append(
        "where your <your-keyword> is the keyword from the text that you found."
    )
    prompt = "".join(prompt_lst)

    response = str(openai.generate(prompt)).strip()
    logger.info(f"GPT response: {response}")
    try:
        response_json = json.loads(response)
    except ValueError:
        logger.info("Response was not valid JSON format.")
        return ""
    return response_json.get("keyword", "")

>>>>>>> upstream/main

def submit_app(config, logger):
    with sync_playwright() as p:
        browser, page = build_context(p, config, logger)
        
        try:
            # remove cookie popup
            remove_cookies_popup(page)

            # check my account button - using force=True to bypass interception
            # try multiple times if the login input doesn't appear
            login_button = page.get_by_role("button", name="Mein Konto").or_(page.get_by_text("Mein Konto")).first
            login_email = page.locator("#login_email_username")

<<<<<<< HEAD
            for i in range(3):
                login_button.click(force=True)
                try:
                    login_email.wait_for(state="visible", timeout=5000)
                    break 
                except:
                    if i == 2:
                        logger.error("Login modal did not appear after 3 attempts.")
                        browser.close()
                        return False
                    logger.warning(f"Login modal not visible, retry {i+1}...")
                    remove_cookies_popup(page)

            # enter credentials
            login_email.fill(config["wg_gesucht_credentials"]["email"])
            page.locator("#login_password").fill(config["wg_gesucht_credentials"]["password"])
=======
    # create the ChromeDriver object and log
    try:
        service_log_path = "chromedriver.log"
        service_args = ["--verbose"]
        driver = webdriver.Chrome(
            service=Service(executable_path=config["chromedriver_path"]),
            options=chrome_options,
            service_args=service_args,
            service_log_path=service_log_path,
        )
        if not config["run_headless"]:
            driver.maximize_window()
        driver.get("https://www.wg-gesucht.de/nachricht-senden" + config["ref"])
    except Exception as e:
        logger.info(
            "Chrome crashed! You might be trying to run it without a screen in terminal?"
        )
        raise e

    # # accept cookies button
    # click_button(driver, By.XPATH, "//*[contains(text(), 'Accept all')]")
    # click_button(driver, By.XPATH, "//*[contains(text(), 'Akzeptieren')]")
    # instead of accepting cookies, just remove cookie popup,
    # as "Akzeptieren" doesn't show on headless Firefox on Linux for some reason
    remove_cookies_popup(driver)
>>>>>>> upstream/main

            # click login button and wait for redirect
            page.locator("#login_submit").click()
            
            # wait for message input to be visible again (means we are back on the app page)
            try:
                page.locator("#message_input, textarea[name='message'], textarea#message_input, .conversation-input textarea").first.wait_for(state="visible", timeout=10000)
                logger.info("Logged in and back on submission page.")
            except:
                logger.warning("Timed out waiting for message input after login. Proceeding anyway...")

            # remove the occasional cookie popup again
            remove_cookies_popup(page)
            remove_lightbox(page)

            # accept the occasional advice gives on how to stay safe
            try:
                # Using a more robust locator for the confirmation button
                safety_confirm = page.locator("#sicherheit_bestaetigung").or_(page.get_by_role("button", name=re.compile("bestätigen|verstanden", re.IGNORECASE)))
                safety_confirm.click(timeout=2000)
            except:
                pass

            # checks if a message has already been sent previously to listing
            if page.locator("#message_timestamp").is_visible(timeout=2000):
                logger.info("Message has already been sent previously. Will skip this offer.")
                browser.close()
                return False

<<<<<<< HEAD
            logger.info(f"Sending to: {config['user_name']}, {config['address']}.")
=======
    remove_cookies_popup(driver)

    # remove lightbox div that blocks attachments
    divs_to_remove = driver.find_elements(By.XPATH, "//div[@class='lightbox']")
    for div in divs_to_remove:
        driver.execute_script("arguments[0].remove();", div)

    # occasionally wg-gesucht gives you advice on how to stay safe.
    try:
        click_button(driver, By.ID, "sicherheit_bestaetigung")
    except:
        logger.info("No security check.")
>>>>>>> upstream/main

            # get message area locator - using more robust multiple selectors
            text_area = page.locator("#message_input, textarea[name='message'], textarea#message_input, .conversation-input textarea").first

            # read message from config
            try:
                message = config.get("message", "")
                if not message:
                    logger.error("No 'message' found in config!")
                    browser.close()
                    return False
                
                message = message.replace("recipient", config["user_name"].split(" ")[0])

                # use GPT to check ads for "if you've read this write X"
                if config.get("openai_key"):
                    getter = ListingInfoGetter(config["ref"])
                    text = getter.get_listing_text()

                    client = OpenAI(api_key=config["openai_key"])
                    completion = client.completions.create(
                        model="gpt-3.5-turbo-instruct",
                        max_tokens=2000,
                        prompt=f"""
                        Du bist dabei, eine Nachricht auf WG-Gesucht an "{config['user_name']}" über ein Angebot mit folgender Beschreibung zu senden:
                        "{text}"
                        Deine Nachricht lautet:
                        "{message}"
                        Sorge dafür, dass die Nachricht entsprechend der Beschreibung angepasst ist.
                        Gib als Antwort nur die Nachricht an.
                        """
                    )
                    message = completion.choices[0].text

                # fill message with a small delay for stability
                # wait for the text area to be attached and visible
                text_area.wait_for(state="visible", timeout=10000)
                text_area.fill(message)
                page.wait_for_timeout(500)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                browser.close()
                return False

            if config.get("attach_schufa"):
                # open the attachment popup
                # Trying to find the attachment button by text or icon classes
                attachment_btn = page.get_by_role("button", name=re.compile("anhang|anhängen", re.IGNORECASE)).or_(page.locator(".btn.wgg_white.pull-right.mr10")).first
                attachment_btn.click()
                
                # at the popup, open the file attachment selection
                file_opt = page.get_by_text(re.compile("datei|file", re.IGNORECASE)).or_(page.locator(".attach_file")).first
                file_opt.wait_for(state="visible")
                file_opt.click()
                
                # select the document named "SCHUFA-BonitaetsCheck.pdf"
                schufa_doc = page.get_by_text("SCHUFA-BonitaetsCheck.pdf")
                schufa_doc.wait_for(state="visible")
                schufa_doc.click()
                
                # close attachment (click outside or press Escape)
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                # Fallback click if Escape didn't work (some modals are stubborn)
                page.mouse.click(10, 10)

            # wait a bit for stability
            page.wait_for_timeout(2000)

<<<<<<< HEAD
            # click send button
            try:
                # find and click submit button - searching for Senden or Nachricht senden, following the class from screenshot
                submit_button = page.locator("button.conversation_send_button, #send_message, #message_send_button, button[name='send'], button:has-text('Senden'), button:has-text('Nachricht senden')").first
                submit_button.click(force=True)
                logger.info(f">>>> Message sent to: {config['ref']} <<<<")
                page.wait_for_timeout(2000)
                browser.close()
                return True
            except:
                logger.error("Cannot find submit button!")
                browser.close()
                return False
                
        except Exception as e:
            logger.error(f"Error during submission: {e}")
            browser.close()
            return False
=======
    # read message from a file
    try:
        with open(message_file, "r") as file:
            message = str(file.read())
        message = message.replace("receipient", config["user_name"].split(" ")[0])
        # if "keyword" in locals() and keyword != "":
        #     message = f"{keyword}\n\n" + message
        text_area.send_keys(message)
    except:
        logger.info(f"{message_file} file not found!")
        driver.quit()
        return False

    driver.implicitly_wait(2)

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
>>>>>>> upstream/main
