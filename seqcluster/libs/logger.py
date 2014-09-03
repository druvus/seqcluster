import logging
from colorlog import ColoredFormatter
import os.path


def getLogger(name):
    return logging.getLogger(__name__)


def initialize_logger(output_dir):
    NOTE = 15
    COLOR_FORMAT = "%(log_color)s%(levelname)s-%(name)s(%(lineno)d)%(reset)s: %(message)s"
    COLOR_FORMAT_INFO = "%(log_color)s%(levelname)s%(reset)s: %(message)s"
    FORMAT = "%(levelname)s-%(name)s(%(lineno)d): %(message)s"
    FORMAT_INFO = "%(levelname)s %(message)s"
    logging.addLevelName(NOTE, "NOTE")

    def note(self, message, *args, **kws):
        self.log(NOTE, message, *args, **kws)
    logging.Logger.note = note
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    #create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = ColoredFormatter(COLOR_FORMAT_INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

   # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"),"w", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = ColoredFormatter(COLOR_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "run.log"), "w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "trace.log"),"w")
    handler.setLevel(NOTE)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)