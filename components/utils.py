import logging
import os


def get_logger():
    level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger = logging.getLogger(__file__)
    logger.setLevel(level)
    if not logger.handlers:
        if os.environ.get('CONTAINER_LOGGING', 'false') == 'true':
            handler = logging.FileHandler('/var/log/container_logs.log')
        else:
            handler = logging.StreamHandler()
        if (log_format := os.environ.get('LOG_FORMAT')) is not None:
            formatter = logging.Formatter(log_format, os.environ.get('LOG_DATE_FORMAT'))
            handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
    return logger
