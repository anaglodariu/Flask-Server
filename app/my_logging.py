'''
module my_logging.py
'''
from logging import getLogger, Formatter, INFO
from logging.handlers import RotatingFileHandler
from time import gmtime

class CustomLogging:
    '''
    custom class for logging
    '''
    def __init__(self, max_bytes = 10000, backup_count = 1):
        '''
        create a rotating file handler for logging to webserver.log
        '''

        # create logger
        self.logger = getLogger(__name__)
        self.logger.setLevel(INFO)

        # create a rotating file handler
        handler = RotatingFileHandler('webserver.log', max_bytes, backup_count)
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # set the formatter to use gmtime
        formatter.converter = gmtime
        handler.setFormatter(formatter)
        handler.setLevel(INFO)

        # add the handler to the logger
        self.logger.addHandler(handler)

    def get_logger(self):
        '''
        return the logger instance
        '''
        return self.logger
