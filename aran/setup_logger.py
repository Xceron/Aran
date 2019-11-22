import logging

from aran.colors import Color as Col


class ColorFormatter(logging.Formatter):
    """
    Inherits from Formatter to allow for custom logging messages.
    Taken from https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3
    """
    error_format = f"ERROR:%(asctime)s:%(name)s:%(message)s"
    debug_format = f"{Col.WARNING} %(asctime)s:%(name)s:%(message)s"
    info_format = f"{Col.OK} %(message)s"
    
    def __init__(self):
        super(ColorFormatter, self).__init__(fmt="%(asctime)s:%(name)s:%(message)s", datefmt=None, style="%")

    def format(self, record):
        original_format = self._style._fmt

        if record.levelno == logging.ERROR:
            self._style._fmt = ColorFormatter.error_format
        elif record.levelno == logging.DEBUG:
            self._style._fmt = ColorFormatter.debug_format
        if record.levelno == logging.INFO:
            self._style._fmt = ColorFormatter.info_format

        combined_format = logging.Formatter.format(self, record)
        self._style._fmt = original_format
        return combined_format


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = ColorFormatter()
file_handler = logging.FileHandler("aran.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)