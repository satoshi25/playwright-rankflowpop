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

def convert_time_format(sec):
    sec %= 24 * 3600
    hour = sec // 3600
    sec %= 3600
    minute = sec // 60
    sec %= 60
    return f"{hour}시간 {minute}분 {sec}초"
