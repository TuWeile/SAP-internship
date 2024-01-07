from helper.common_helper import CommonHelper
from helper.logger_helper import LoggerHelper


class BaseHandler:
    def __init__(self, message, logfile):
        self.done = False
        self.logger = LoggerHelper(logfile)
        self.message = message

        self.helper = CommonHelper()
