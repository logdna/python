import sys
import time
import json
from .configs import defaults
import logging
import requests

from threading import Timer
from socket import gethostname

class LogDNAHandler(logging.Handler):
    def __init__(self, token, options={}):
        self.buf = []
        logging.Handler.__init__(self)
        self.token = token
        self.hostname = options['hostname'] if 'hostname' in options else gethostname()
        self.level = options['level'] if 'level' in options else 'info'
        self.app = options['app'] if 'app' in options else ''
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

    def bufferLog(self, message):
        if message and message['line']:
            if self.max_length and len(message['line']) > defaults['MAX_LINE_LENGTH']:
                message['line'] = message['line'][:defaults['MAX_LINE_LENGTH']] + ' (cut off, too long...)'
                print('Line was longer than ' + defaults['MAX_LINE_LENGTH'] + ' chars and was truncated.')

            self.bufByteLength += sys.getsizeof(message)
            self.buf.append(message)

            if self.bufByteLength >= self.flushLimit:
                self.flush()
                return

            if not self.flusher:
                self.flusher = Timer(defaults['FLUSH_INTERVAL'], self.flush())

    def flush(self):
        if not self.buf or len(self.buf) < 0:
            return
        data = {'e': 'ls', 'ls': self.buf}
        resp = requests.post(url=defaults['LOGDNA_URL'], json=data, auth=('user', self.token), params={ 'hostname': self.hostname }, stream=True)
        # print(self.buf)
        self.buf = []
        self.bufByteLength = 0
        if self.flusher:
            self.flusher.cancel()
            self.flusher = None

    def emit(self, record):
        record = record.__dict__
        opts = {}
        if 'args' in record:
            opts = record['args']
        message = {
            'hostname' : self.hostname,
            'timestamp': int(time.time()),
            'line': record['msg'],
            'level': record['levelname'] or self.level,
            'app': self.app or record['module']
        }
        if 'level' in opts:
            message['level'] = opts['level']
        if 'app' in opts:
            message['app'] = opts['app']
        if 'hostname' in opts:
            message['hostname'] = opts['hostname']
        if 'timestamp' in opts:
            message['timestamp'] = opts['timestamp']
        if 'context' in opts:
            if self.index_meta:
                message['meta'] = opts['context']
            else:
                message['meta'] = json.dumps(opts['context'])

        self.bufferLog(message)

    def close(self):
        logging.Handler.close(self)
