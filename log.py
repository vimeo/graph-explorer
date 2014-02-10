import logging

f = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def make_logger(logger_name, config):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    chandler = logging.StreamHandler()
    chandler.setFormatter(f)
    logger.addHandler(chandler)

    if config.log_file:
        fhandler = logging.FileHandler(config.log_file)
        fhandler.setFormatter(f)
        logger.addHandler(fhandler)
    return logger
