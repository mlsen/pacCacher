import logging

# Logging levels
levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
    }

# Logging Output Config
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')
ch.setFormatter(formatter)

def getLogger(name = None, level = 'WARNING'):

    logger = logging.getLogger(name)
    logger.setLevel(levels[level])
    logger.addHandler(ch)

    return logger
