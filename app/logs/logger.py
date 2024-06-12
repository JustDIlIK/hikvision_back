import logging
import logging.config
import os
from colorlog import ColoredFormatter


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


def get_logger(name):
    logging.config.dictConfig(LOGGING_CONFIG)

    logger = logging.getLogger(name)
    log_file_path = os.path.join(os.path.dirname(__file__), f"{name}.log")
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "Время: %(asctime)s\n"
            "Модуль: %(name)s\n"
            "Тип: %(levelname)s\n"
            "Текст: %(message)s\n"
        )
    )

    logger.addHandler(file_handler)
    return logger
