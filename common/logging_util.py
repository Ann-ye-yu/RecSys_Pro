import logging
from common.config import LOGGING_FILE_PATH,LOG_LEVEL

logger = logging.getLogger("recallApp")
logger.setLevel(level = LOG_LEVEL)

handler = logging.FileHandler(LOGGING_FILE_PATH)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')
handler.setFormatter(formatter)
 
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
 
logger.addHandler(handler)
logger.addHandler(console)
logger.info("init logging config")
print("log load ok")