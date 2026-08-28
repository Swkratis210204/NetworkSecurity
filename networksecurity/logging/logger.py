import logging
import os
from datetime import datetime

# Creates a unique log filename based on the current timestamp (Month_Day_Year_Hour_Minute_Second.log)
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Defines the path for a dedicated folder inside 'logs' named after this run's timestamp
logs_path = os.path.join(os.getcwd(), "logs", LOG_FILE)

# Creates the target directory if it does not exist already
os.makedirs(logs_path, exist_ok=True)

# Full path to the log file inside the timestamped directory
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configures the global logging settings: target file, structured message format, and logging threshold
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)