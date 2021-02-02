import logging
from threading import Thread

__all__ = ['logger', 'info', 'LOGDNA_API_KEY']
LOGDNA_API_KEY = '< YOUR INGESTION KEY HERE >'
logger = logging.getLogger('logdna')
logger.setLevel(logging.INFO)


def info(*args):
    def fn():
        for line in args:
            logger.info(line)

    thread = Thread(target=fn)
    thread.setDaemon(True)
    thread.start()
    return thread
