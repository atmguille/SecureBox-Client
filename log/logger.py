import logging
import logging.config

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL,
          'not set': logging.NOTSET}


def set_logger(args):
    if args.log_config:
        logging.config.fileConfig(fname='log/logging.ini', disable_existing_loggers=False)
        logger = logging.getLogger(__name__)
    else:
        level = LEVELS.get(args.log_level, logging.NOTSET)
        str_format = '%(asctime)s [%(levelname)s] - %(message)s'
        logging.basicConfig(level=level, format=str_format)
        logger = logging.getLogger(__name__)
        if args.log_file:
            if type(args.log_file) == str:
                file_handler = logging.FileHandler(args.log_file, mode="w")
            else:
                file_handler = logging.FileHandler("log/file.log", mode="w")
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(str_format))
            logger.addHandler(file_handler)
    return logger


def get_logger():
    return logging.getLogger(__name__)