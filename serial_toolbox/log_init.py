import logging, coloredlogs, sys

def log_init(log_level: int = logging.ERROR):
    """
    Function to initialize the logger. Sets up the logger to output INFO
    level logs to stdout with a certain message format. The format includes 
    time, logging level, and the message.

    Parameters
    ----------
    log_level : int, optional
        The logging level, by default logging.ERROR

    Returns
    -------
    logging.RootLogger
        The initialized logger.
    """
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
    logger.setLevel(log_level)
    coloredlogs.install(level=log_level, logger=logger)
    logger.info("logger setup done.")
    return logger