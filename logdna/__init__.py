from .logdna import LogDNAHandler
__all__ = ['LogDNAHandler']
__VERSION__ = "1.5.4"
# Publish this class to the "logging.handlers" module so that it can be use
# from a logging config file via logging.config.fileConfig().
import logging.handlers

logging.handlers.LogDNAHandler = LogDNAHandler
