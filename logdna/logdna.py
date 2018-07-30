import sys
import time
import json
from .configs import defaults
import logging
import requests
import threading
import socket
from threading import Timer
logger = logging.getLogger(__name__)

class LogDNAHandler(logging.Handler):
    def __init__(self, key, options={}):
        self.buf = []
        self.secondary = []
        logging.Handler.__init__(self)
        self.key = key
        self.hostname = options['hostname'] if 'hostname' in options else socket.gethostname()
        self.ip = options['ip'] if 'ip' in options else self.get_ip()
        self.mac = options['mac'] if 'mac' in options else None
        self.level = options['level'] if 'level' in options else 'info'
        self.app = options['app'] if 'app' in options else ''
        self.env = options['env'] if 'env' in options else ''
        self.setLevel(logging.DEBUG)

        self.tags = []
        if 'tags' in options and isinstance(options['tags'], list):
            self.tags.extend(options['tags'])
        self.max_length = True
        if 'max_length' in options:
            self.max_length = options['max_length']
        self.index_meta = False
        if 'index_meta' in options:
            self.index_meta = options['index_meta']
        self.include_standard_meta = False
        if 'include_standard_meta' in options:
            self.include_standard_meta = options['include_standard_meta']
        self.flushLimit = defaults['FLUSH_BYTE_LIMIT']
        self.url = defaults['LOGDNA_URL']
        self.bufByteLength = 0
        self.flusher = None
        self.lock = threading.RLock()
        self.request_timeout = defaults['MAX_REQUEST_TIMEOUT']
        if 'request_timeout' in options:
            self.request_timeout = options['request_timeout']

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
                resp = requests.post(
                    url=defaults['LOGDNA_URL'],
                    json=data,
                    auth=('user', self.key),
                    params={
                        'hostname': self.hostname,
                        'ip': self.ip,
                        'mac': self.mac if self.mac else None,
                        'tags': self.tags if self.tags else None},
                    stream=True,
                    timeout=self.request_timeout)
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
        if self.include_standard_meta:
            if isinstance(opts, tuple):
                opts = {}
            if 'meta' not in opts:
                opts['meta'] = {}
            for key in ['name', 'pathname', 'lineno']:
                opts['meta'][key] = record[key]

        message = {
            'hostname': self.hostname,
            'timestamp': int(time.time() * 1000),
            'line': msg,
            'level': record['levelname'] or self.level,
            'app': self.app or record['module'],
            'env': self.env
        }
        if not isinstance(opts, tuple):
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

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def close(self):
        """
        Close the log handler.

        Make sure that the log handler has attempted to flush the log buffer before closing.
        """
        try:
            self.flush()
        finally:
            logging.Handler.close(self)
