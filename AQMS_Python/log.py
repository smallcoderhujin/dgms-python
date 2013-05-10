import logging

def writeErrorLogger(message):
    logger = logging.getLogger()
    handler = logging.FileHandler('D:\hujin\DMMS\log.txt')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    logger.error(message)
    handler.flush()
    logger.removeHandler(handler)

def writeInfoLogger(message):
    logger = logging.getLogger()
    handler = logging.FileHandler('D:\hujin\DMMS\log.txt')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info(message)
    handler.flush()
    logger.removeHandler(handler)