import sys
import time
import json
from .configs import defaults
import logging
import requests
import threading
from threading import Timer
from socket import gethostname
logger = logging.getLogger(__name__)

class LogDNAHandler(logging.Handler):
    def __init__(self, token, options={}):
        self.buf = []
        self.secondary = [];
        logging.Handler.__init__(self)
        self.token = token
        self.hostname = options['hostname'] if 'hostname' in options else gethostname()
        self.level = options['level'] if 'level' in options else 'info'
        self.app = options['app'] if 'app' in options else ''
        self.env = options['env'] if 'env' in options else ''
        self.setLevel(logging.DEBUG)

        self.max_length = True
        if 'max_length' in options:
            self.max_length = options['max_length']
        self.index_meta = False
        if 'index_meta' in options:
            self.index_meta = options['index_meta']
        self.flushLimit = defaults['FLUSH_BYTE_LIMIT']
        self.url = defaults['LOGDNA_URL']
        self.bufByteLength = 0
        self.flusher = None
        self.lock = threading.RLock()

    def bufferLog(self, message):
        if message and message['line']:
            if self.max_length and len(message['line']) > defaults['MAX_LINE_LENGTH']:
                message['line'] = message['line'][:defaults['MAX_LINE_LENGTH']] + ' (cut off, too long...)'
                logger.debug('Line was longer than ' + str(defaults['MAX_LINE_LENGTH']) + ' chars and was truncated.')

        self.bufByteLength += sys.getsizeof(message)

        # Attempt to acquire lock to write to buf, otherwise write to secondary as flush occurs
        if not self.lock.acquire(blocking=False):
            self.secondary.append(message)
        else:
            self.buf.append(message)
            self.lock.release();
            if self.bufByteLength >= self.flushLimit:
                self.flush()
                return

        if not self.flusher:
            self.flusher = Timer(defaults['FLUSH_INTERVAL'], self.flush)
            self.flusher.start()

    def flush(self):
        if not self.buf or len(self.buf) < 0:
            return
        data = {'e': 'ls', 'ls': self.buf}
        try:
            # Ensure we have the lock when flushing
            if not self.lock.acquire(blocking=False):
                if not self.flusher:
                    self.flusher = Timer(defaults['FLUSH_NOW'], self.flush)
                    self.flusher.start()
            else:
                resp = requests.post(url=defaults['LOGDNA_URL'], json=data, auth=('user', self.token), params={ 'hostname': self.hostname }, stream=True, timeout=defaults['MAX_REQUEST_TIMEOUT'])
                self.buf = []
                self.bufByteLength = 0
                if self.flusher:
                    self.flusher.cancel()
                    self.flusher = None
                self.lock.release();
                # Ensure messages that could've dropped are appended back onto buf
                self.buf = self.buf + self.secondary;
                self.secondary = [];
        except requests.exceptions.RequestException as e:
            if self.flusher:
                self.flusher.cancel()
                self.flusher = None
            self.lock.release();
            logger.error('Error in request to LogDNA: ' + str(e))

    def isJSONable(self, obj):
        try:
            json.dumps(obj)
            return True
        except:
            return False

    def sanitizeMeta(self, meta):
        keysToSanitize = []
        for key,value in meta.items():
            if not self.isJSONable(value):
                keysToSanitize.append(key)
        if keysToSanitize:
            for key in keysToSanitize:
                del meta[key]
            meta['__errors'] = 'These keys have been sanitized: ' + ', '.join(keysToSanitize)
        return meta

    def emit(self, record):
        msg = self.format(record)
        record = record.__dict__
        opts = {}
        if 'args' in record:
            opts = record['args']
        message = {
            'hostname' : self.hostname,
            'timestamp': int(time.time()),
            'line': msg,
            'level': record['levelname'] or self.level,
            'app': self.app or record['module'],
            'env': self.env
        }
        if 'level' in opts:
            message['level'] = opts['level']
        if 'app' in opts:
            message['app'] = opts['app']
        if 'hostname' in opts:
            message['hostname'] = opts['hostname']
        if 'env' in opts:
            message['env'] = opts['env']
        if 'timestamp' in opts:
            message['timestamp'] = opts['timestamp']
        if 'meta' in opts:
            if self.index_meta:
                message['meta'] = self.sanitizeMeta(opts['meta'])
            else:
                message['meta'] = json.dumps(opts['meta'])

        self.bufferLog(message)

    def close(self):
        """
        Close the log handler.

        Make sure that the log handler has attempted to flush the log buffer before closing.
        """
        try:
            self.flush()
        finally:
            logging.Handler.close(self)
