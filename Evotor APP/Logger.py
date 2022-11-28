import logging
import logging.config
import os
from Classes import MainClass


class CustomFilter(logging.Filter):
    """
    Painting differently important messages

    class CustomFilter(logging.Filter)
        def filter(self, record)
    """
    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "WHITE",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED"
    }

    def filter(self, record):
        record.color = CustomFilter.COLOR[record.levelname]
        return True


class LogData(MainClass):
    """
    Pulling some Data or Info about Errors to the Log-file and stream

    class LogData
        def get_logger(self, level='INFO')
        def set_log_level(level='INFO')
    """
    def __init__(self):
        super().__init__()
        self.name = "class LogData(MainClass)"
        self.description = "Логирование обмена данными между сервером пользователя и облаком Эвотор"
        self.logfile_name = 'main_log.log'
        self.logfile_path = os.path.abspath('')
        self.log_format_short = f"%(asctime)s - [%(levelname)s] - %(message)s"
        self.log_format_full = f"%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"

    def get_logger(self, module_name, level='INFO'):
        """
        :param module_name:
        :param level:
        :return: logger
        """
        logger = logging.getLogger(module_name)
        logging.LoggerAdapter(logger, {"app": self.get_description()})
        logger.setLevel(self.set_log_level(level))

        file_handler = logging.FileHandler(self.logfile_name)
        file_handler.setLevel(self.set_log_level(level))
        file_handler.setFormatter(logging.Formatter(self.log_format_full))
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(self.log_format_short))
        logger.addHandler(stream_handler)

        return logger

    @staticmethod
    def set_log_level(level='INFO'):
        if level == 'WARNING':
            return logging.WARNING
        elif level == 'ERROR':
            return logging.ERROR
        return logging.INFO

    def put_log_message(self, message, name='', level='INFO'):
        logger = self.get_logger(name, level='INFO')
        logger.info(message)
