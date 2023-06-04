import json
import logging
import os.path
import time
from argparse import ArgumentParser
from datetime import datetime
from subprocess import call

import submit_wg

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")


def scrape_site():
    call(
        [
            "scrapy",
            "crawl",
            "wg-gesucht",
            "-o",
            "wg_offer.json",
            "-s",
            "LOG_ENABLED=false",
        ]
    )
    with open("wg_offer.json", "r") as data_file:
        data = json.load(data_file)
    data = list(set([i["data-id"] for i in data]))
    if os.path.isfile("wg_offer_old.json"):
        with open("wg_offer_old.json", "r") as data_old_file:
            if len(data_old_file.readlines()) != 0:
                data_old_file.seek(0)
                data_old = json.load(data_old_file)
            else:
                data_old = []
        data_old = list(set([i["data-id"] for i in data_old]))
    else:
        data_old = []
    return data, data_old


def clear_json_files():
    files = ["wg_offer.json", "wg_offer_old.json"]
    for file in files:
        with open(file, "w") as f:
            json.dumps({})


def main(args):
    clear_json_files()
    fname = "wg_offer.json"
    while True:
        if os.path.isfile(fname):
            logger.info("Scrape wg-gesucht.de for new offers.")
            call(["mv", fname, "wg_offer_old.json"])
            data, data_old = scrape_site()
        else:
            logger.info("No 'wg_offer.json' file found.")
            data, data_old = scrape_site()

        if not os.path.isfile("messages_sent.txt"):
            with open("messages_sent.txt", "w") as f:
                pass

        diff_id = list(set(data) - set(data_old))
        with open("messages_sent.txt", "r") as msgs:
            messages_sent = msgs.readlines()
        if len(diff_id) != 0:
            logger.info(f"Found {len(diff_id)} new offers.")
            for new in diff_id:
                # avoid messaging letting agencies
                if len(new.split("/")) > 2:
                    continue
                logger.info(f"Trying to send message to: {new}")
                info_to_store = submit_wg.submit_app(new, logger, args, messages_sent)
                if info_to_store:
                    with open("messages_sent.txt", "a") as msgs:
                        msgs.write(f"{info_to_store}\n")
        else:
            logger.info("No new offers.")
        logger.info("Sleep.")
        time.sleep(5)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--launch_type", type=str, default="headless")
    parser.add_argument("--min_rental_period", type=int, default=6)
    args = parser.parse_args()
    main(args)