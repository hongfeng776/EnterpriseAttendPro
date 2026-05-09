import logging
import os
from datetime import datetime
from src.config.settings import LOG_DIR


class SystemLogger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        self._logger = logging.getLogger("AttendanceSystem")
        self._logger.setLevel(logging.DEBUG)

        log_filename = os.path.join(
            LOG_DIR, f"system_{datetime.now().strftime('%Y%m%d')}.log"
        )

        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)

    def critical(self, message):
        self._logger.critical(message)


logger = SystemLogger()
