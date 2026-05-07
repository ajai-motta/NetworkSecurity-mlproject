import os
import logging
from datetime import datetime

LOGFILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
logs_path=os.path.join(os.getcwd(),"logs")
os.makedirs(logs_path,exist_ok=True)
LOG_FILE_PATH=os.path.join(logs_path,LOGFILE)
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
    level=logging.INFO
)
