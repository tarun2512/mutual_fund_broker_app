import logging
import os
from logging import StreamHandler
from logging.handlers import RotatingFileHandler, SocketHandler

import yaml

from scripts.config import PathToStorage, Service


# this method is to read the configuration from backup.conf
def read_configuration(file_name):
    """
    :param file_name:
    :return: all the configuration constants
    """
    with open(file_name) as stream:
        try:
            return yaml.safe_load(stream)
        except Exception as e:
            print(f"Failed to load Configuration. Error: {e}")


config = read_configuration("scripts/logging/logger_conf.yml")

logging_config = config["logger"]
logging_config["level"] = Service.LOG_LEVEL


def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `level_name` becomes an attribute of the `logging` module with the value
    `level_num`. `method_name` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `method_name` is not specified, `level_name.lower()` is
    used.

    To avoid accidental clobbering of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    > add_logging_level('TRACE', logging.DEBUG - 5)
    > logging.getLogger(__name__).setLevel("TRACE")
    > logging.getLogger(__name__).trace('that worked')
    > logging.trace('so did this')
    > logging.TRACE

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError("{} already defined in logging module".format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError("{} already defined in logging module".format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError("{} already defined in logger class".format(method_name))

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


def get_logger():
    """
    Creates a rotating log
    """
    __logger__ = logging.getLogger("ilens")
    add_logging_level("QTRACE", logging.DEBUG - 5)
    __logger__.setLevel(logging_config["level"].upper())
    log_formatter = "%(asctime)s - %(levelname)-6s - [%(threadName)5s:%(funcName)5s():" + "%(lineno)s] - %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S"
    file_path = PathToStorage.LOGS_MODULE_PATH
    formatter = logging.Formatter(log_formatter, time_format)

    for each_handler in logging_config["handlers"]:
        if each_handler["type"] in ["RotatingFileHandler"] and Service.ENABLE_FILE_LOG:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            log_file = os.path.join(file_path, f"{logging_config['name']}.log")
            temp_handler = RotatingFileHandler(
                log_file, maxBytes=each_handler["max_bytes"], backupCount=each_handler["back_up_count"]
            )
            temp_handler.setFormatter(formatter)
        elif each_handler["type"] in ["SocketHandler"]:
            temp_handler = SocketHandler(each_handler["host"], each_handler["port"])
        elif each_handler["type"] in ["StreamHandler"] and Service.ENABLE_CONSOLE_LOG:
            temp_handler = StreamHandler()
            temp_handler.setFormatter(formatter)
        else:
            temp_handler = None
        if temp_handler:
            __logger__.addHandler(temp_handler)

    return __logger__


logger = get_logger()
