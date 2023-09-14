import logging


log_file = "error.log"
logger = logging.getLogger("error_logger")
logger.setLevel(logging.ERROR)

log_handler = logging.FileHandler(log_file)
log_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)
