from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import logging
import pprint

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")


class ListingGetter:
    def __init__(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=0)  # millisecond timeout
            html = page.inner_html("#main_column")

        soup = BeautifulSoup(html, "lxml")

        # Find all <p> tags on the page
        p_tags = soup.find_all("p")

        # Check for the word "Captchas" in <p> tags and log when found
        for p_tag in p_tags:
            if "Captchas" in p_tag.get_text():
                # Log the occurrence of "Captchas" within <p> tags
                logger.critical("Captcha detected. Retrying...")
                break

        # get all listing elements by looking for 'liste-details-ad-#####'
        self.listings = soup.find_all("div", id=re.compile("^liste-details-ad-\d+"))

    def get_all_infos(self):
        info_dict = {}
        refs = self.get_refs()
        user_names = self.get_users()
        addresses, wg_types = self.get_address_wg()
        rental_lengths_months = self.get_rental_length_months()

        # ensure all list are the same length
        lists = [refs, user_names, addresses, wg_types, rental_lengths_months]
        it = iter(lists)
        the_len = len(next(it))
        if not all(len(l) == the_len for l in it):
            raise ValueError("Not all lists have the same length!")

        # write dict for all listings
        for i, (ref, user_name, address, wg_type, rental_length_months) in enumerate(
                zip(refs, user_names, addresses, wg_types, rental_lengths_months)):

            # skip promotes offers from letting agencies
            if "\n" in user_name:
                continue

            listing_dict = {"ref": ref, "user_name": user_name, "address": address, "wg_type": wg_type,
                            "rental_length_months": rental_length_months}
            info_dict[i] = listing_dict
        return info_dict

    def get_refs(self):
        refs = list()
        for listing in self.listings:
            element = listing.find("a", href=True)
            refs.append(element["href"])
        return refs

    def get_users(self):
        users = list()
        for listing in self.listings:
            element = listing.find("span", {"class": "ml5"})
            users.append(element.getText())
        return users

    def get_address_wg(self):
        address = list()
        wg_type = list()
        for listing in self.listings:
            element = listing.find("div", {"class": "col-xs-11"})
            text = element.find("span").getText()
            parts = [part.strip() for part in re.split("\||\n", text) if part.strip() != ""]
            wg_type.append(parts[0])
            address.append(", ".join(parts[::-1][:-1]))
        return address, wg_type

    def get_rental_length_months(self):
        rental_length_months = list()
        for listing in self.listings:
            element = listing.find("div", {"class": "col-xs-5 text-center"})
            text = element.getText()
            start_end = [part.strip() for part in re.split("-|\n", text) if part.strip() != ""]
            rental_length_months.append(self._get_rental_length_months("-".join(start_end)))
        return rental_length_months

    @staticmethod
    def _get_rental_length_months(date_range_str: str) -> int:
        dates = date_range_str.split("-")
        if len(dates) != 2:
            # means listing is 'unbefristet'
            return -1
        start, end = date_range_str.split("-")
        start, end = start.strip(), end.strip()

        # year, month, day
        start_day, start_month, start_year = start.split(".")
        end_day, end_month, end_year = end.split(".")

        # get time difference in months
        date_diff = (int(end_year) - int(start_year)) * 12 + (
                int(end_month) - int(start_month)
        )
        return date_diff
