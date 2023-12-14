import time
import logging

import yaml
from wg_gesucht import main

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")

with open("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)

while True:
    try:
        main(config)
    except Exception as e:
        logger.exception(e)
        logger.critical("Restarting in 60 seconds...")
        time.sleep(60)
