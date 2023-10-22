import platform
import subprocess
import time
import os
import logging

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")

# Determine the correct directory ('Scripts' for Windows, 'bin' for Linux)
if platform.system() == 'Windows':
    venv_executable_dir = 'Scripts'
    start = "venv"
else:
    venv_executable_dir = 'bin'
    start = "env"

# Set the Python executable within the virtual environment
python_command = os.path.join(start, venv_executable_dir, 'python')

# Set the working directory to where wg-gesucht.py is located
project_directory = os.path.dirname(os.path.abspath(__file__))  # Use the directory of main.py

while True:
    process = None

    try:
        # Start wg-gesucht.py using the virtual environment's Python executable
        process = subprocess.Popen(
            [python_command, 'wg-gesucht.py'],
            cwd=project_directory
        )
        process.wait(timeout=1800)  # Restart script in fixed intervals
    except subprocess.TimeoutExpired as e:
        logger.info("Stopped wg-gesucht.py")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Restarting wg-gesucht.py in 30s...")
        if process is not None:
            process.terminate()
        time.sleep(30)
