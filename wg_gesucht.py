import logging
import os.path
import time

import yaml

from src import ListingGetter, submit_wg

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")


def main(config):
    """
    Operations:
     - Get the newest listings
     - Compares them with previous listing (if available)
     - For all new listings not present in previous listings:
        - Checks rental length of listing
        - Checks if listing is reuploaded by comparing to user_name and address
        - Attempts to submit an application
        - Adds listing to 'past_listings.txt'
    """

    # initialise old listings for later
    old_listings = dict()

    while True:
        # read previously sent messages:
        past_listings_file_name = "past_listings.txt"
        if not os.path.exists(past_listings_file_name):
            prev_listings = []
        else:
            with open(past_listings_file_name, "r", encoding="utf-8", errors="ignore") as msgs:
                prev_listings = msgs.readlines()

        # get current listings
        url = config["url"]
        listing_getter = ListingGetter(url)
        info_dict = listing_getter.get_all_infos()
        new_listings = info_dict

        # get diff: new - old listings
        old_values = old_listings.values()
        diff_dict = {k: v for k, v in enumerate(new_listings.values()) if v not in old_values}
        if diff_dict:
            logger.info(f"Found {len(diff_dict)} new listings.")
            for listing in diff_dict.values():
                # unpack listing dict
                ref = listing["ref"]
                listing_length_months = listing["rental_length_months"]
                user_name = listing["user_name"]
                address = listing["address"]
                wg_type = listing["wg_type"]
                rental_length_months = listing["rental_length_months"]

                # add to config for submit_app function
                config["ref"] = ref
                config["user_name"] = user_name
                config["address"] = address
                logger.info(f"Trying to send message to: {listing}")

                # check if custom condition is not met. An example custom condition would be "user_name != 'John Doe'".
                try:
                    custom_condition = config["custom_condition"]
                    if custom_condition and not eval(custom_condition):
                        logger.info(f"Custom condition not met: {custom_condition}. Skipping ...")
                        continue
                except:
                    pass

                # check rental length, if below min -> skip this listing
                min_rental_length_months = config["min_listing_length_months"]
                if 0 <= listing_length_months < min_rental_length_months:
                    logger.info(
                        f"Rental period of {listing_length_months} months is below required {min_rental_length_months} months. Skipping ..."
                    )
                    continue

                # check if already messaged listing in the past
                listings_sent_identifier = f"{listing['user_name']}: {listing['address']}\n"
                if listings_sent_identifier in prev_listings:
                    logger.info("Listing in 'prev_listings' file, therefore contacted in the past! Skipping ...")
                    continue

                # use selenium to retrieve dynamically loaded info and send message
                submit_wg.submit_app(config, logger)

                # add listing to past_listings.txt
                with open(past_listings_file_name, "a") as msgs:
                    msgs.write(f"{listings_sent_identifier}")
            old_listings = new_listings.copy()
        else:
            logger.info("No new offers.")
        logger.info("Sleep.")
        time.sleep(60)


if __name__ == "__main__":
    with open("config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
    main(config)
