from datetime import datetime
import logging
import coloredlogs
import sys
import os

def log_init(file_log: bool = True, console_log_level: int = logging.WARNING, file_log_level: int = logging.INFO):
    """
    Function to initialize the logger. Sets up the logger to output different log levels
    to stdout and a log file.

    Parameters
    ----------
    file_log : bool, optional
        Determine whether to output log to a file, by default True.
    console_log_level : int, optional
        The logging level for console output, by default logging.WARNING.
    file_log_level : int, optional
        The logging level for file output, by default logging.INFO.

    Returns
    -------
    logging.RootLogger
        The initialized logger.
    """
    # Create and configure root logger
    logger = logging.getLogger()
    logger.handlers = []  # Clearing existing handlers
    logger.propagate = False  # Ensuring that logs don't propagate to avoid duplication

    log_levels = [console_log_level]

    # Console handler
    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
    handler_console.setLevel(console_log_level)
    logger.addHandler(handler_console)

    # File handler
    if file_log:
        # Create a ./log directory if not exists
        if not os.path.exists('./log'):
            os.makedirs('./log')

        # Gets current datetime and format it as filename format
        date_str = datetime.now().strftime("serial%Y%m%d%H%M.log")
        log_file_path = os.path.join('./log', date_str)

        handler_file = logging.FileHandler(log_file_path)
        handler_file.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
        handler_file.setLevel(file_log_level)
        logger.addHandler(handler_file)

        log_levels.append(file_log_level)

    logger.setLevel(min(log_levels))

    # Enable colored logs for console output
    coloredlogs.install(level=console_log_level, logger=logger)

    logger.info("Logger setup done.")
    return logger