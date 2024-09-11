# from https://gist.github.com/hosackm/654d64760e979280e6fb431af999f489

import logging
from colorama import init, Fore, Back
import os

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    # Change this dictionary to suit your coloring needs!
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.RED,
        "ERROR": Fore.RED + Back.WHITE,
        "CRITICAL": Fore.RED + Back.WHITE
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.levelname = color + record.levelname
            record.msg = color + record.msg
        return logging.Formatter.format(self, record)

class ConditionalFormatter(logging.Formatter):
    # from https://stackoverflow.com/questions/34954373/disable-format-for-some-messages
    def format(self, record):
        if hasattr(record, 'simple') and record.simple:
            return record.getMessage()
        else:
            return logging.Formatter.format(self, record)

class loggerClass(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        # sets up logging-to-file
        file_handler = logging.FileHandler("pandown.log", mode="a")
        f_format = ConditionalFormatter(
            # "%(asctime)s: %(name)-18s [%(levelname)-8s] %(message)s")
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
        file_handler.setFormatter(f_format)
        file_handler.setLevel(logging.DEBUG)
        self.addHandler(file_handler)
        
        # sets up logging-to-screen
        # note this needs to be called second, otherwise the ansi
        # colour codes are saved to file. why?
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColorFormatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"))
        console_handler.setLevel(logging.INFO) 
        self.addHandler(console_handler)

def main():
    logging.setLoggerClass(loggerClass)
    logger = logging.getLogger(__name__)
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.debug("This is a debug message")
    logger.error("This is an error message")

    # log.debug("debug message")
	# log.info("info message")
	# log.warning("warning message")
	# log.error("error message")
	# log.critical("critical message")
