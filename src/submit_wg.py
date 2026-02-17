import logging
import time
import re
from playwright.sync_api import sync_playwright, Page
from openai import OpenAI
from src import ListingInfoGetter

def remove_cookies_popup(page: Page):
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

def remove_lightbox(page: Page):
    try:
        page.evaluate("() => { document.querySelectorAll('.lightbox, .modal-backdrop, .modal-open').forEach(el => el.remove()); }")
    except:
        pass

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

            logger.info(f"Sending to: {config['user_name']}, {config['address']}.")

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
                    # The listing_text should already be in config if wg_gesucht.py follows upstream logic
                    text = config.get("listing_text")
                    if not text:
                        getter = ListingInfoGetter(config["ref"])
                        text = getter.get_listing_text()

                    client = OpenAI(api_key=config["openai_key"])
                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        max_tokens=2000,
                        messages=[
                            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
                            {"role": "user", "content": f"""
Du bist dabei, eine Nachricht auf WG-Gesucht an "{config['user_name']}" über ein Angebot mit folgender Beschreibung zu senden:
"{text}"
Deine Nachricht lautet:
"{message}"
Sorge dafür, dass die Nachricht entsprechend der Beschreibung angepasst ist.
Gib als Antwort nur die Nachricht an.
"""}
                        ]
                    )
                    message = completion.choices[0].message.content

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
