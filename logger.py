import logging


log_file = "error.log"
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)

log_handler = logging.FileHandler(log_file)
log_handler.setLevel(logging.ERROR)

base_format = "%(asctime)s - %(levelname)s - %(message)s"

formatter = logging.Formatter(base_format)
log_handler.setFormatter(formatter)

error_logger.addHandler(log_handler)


# ======================================================================================


logging.basicConfig(filename="app.log", level=logging.INFO, format=base_format)

app_logger = logging.getLogger("app_logger")


# ======================================================================================
