import logging
import coloredlogs
import sys
import os
from datetime import datetime
from pathlib import Path

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
    logging.Logger
        The initialized logger.
    """
    # Create and configure the logger
    logger = logging.getLogger(__name__)
    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.propagate = False

    log_levels = [console_log_level]

    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

    # Console handler
    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setFormatter(formatter)
    handler_console.setLevel(console_log_level)
    logger.addHandler(handler_console)

    # File handler
    if file_log:
        log_dir = Path('./log')
        log_dir.mkdir(parents=True, exist_ok=True)

        # Generate log file name with current date and time
        log_file_path = log_dir / datetime.now().strftime("serial%Y%m%d%H%M.log")

        handler_file = logging.FileHandler(log_file_path)
        handler_file.setFormatter(formatter)
        handler_file.setLevel(file_log_level)
        logger.addHandler(handler_file)

        log_levels.append(file_log_level)

    # Set the logger's level to the lowest log level
    logger.setLevel(min(log_levels))

    # Enable colored logs for console output
    coloredlogs.install(level=console_log_level, logger=logger)

    logger.info("Logger setup done.")
    return logger

# Example usage
if __name__ == "__main__":
    logger = log_init()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")