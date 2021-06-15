import logging

from utils.colors import *

parseLevel = lambda x: getattr(logging, x)
DATE_TIME ='%Y-%m-%d %H:%M:%S'
FORMAT = f'{BLUE}%(asctime)s{RESET} - %(color)s%(levelname)s{RESET} - {BLACKB}%(name)s{RESET} - {GREEN}%(method)s{RESET} - %(message)s'

def LoggerFactory(name='root'):
    '''
    Create a custom logger to use colors in the logs.
    '''
    logging.setLoggerClass(Logger)
    logging.basicConfig(format=FORMAT, datefmt=DATE_TIME)
    return logging.getLogger(name=name)

class Logger(logging.getLoggerClass()):

    def __init__(self, name='root', level=logging.NOTSET):
        self.debug_color =  BLUEB
        self.info_color = YELLOWB
        self.error_color = REDB
        self.ok_color = GREENB
        return super().__init__(name, level)

    def debug(self, message, method=''):
        super().debug(message, extra={'color': self.debug_color, 'method': method})

    def info(self, message, method=''):
        super().info(message, extra={'color': self.info_color, 'method': method})

    def error(self, message, method=''):
        super().error(message, extra={'color': self.error_color, 'method': method})

    def ok(self, message, method=''):
        super().error(message, extra={'color': self.ok_color, 'method': method})

    def change_color(self, method, color):
        setattr(self, f"{method}_color", color)
