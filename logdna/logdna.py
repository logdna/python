import sys
import time
import json
import logging
import socket
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from .configs import defaults
from .utils import sanitize_meta, get_ip

logger = logging.getLogger(__name__)

class LogDNAHandler(logging.Handler):
    def __init__(self, key, options={}):
        logging.Handler.__init__(self)

        self.key = key
        self.buf = []
        self.secondary = []
        self.exception_flag = False
        self.buf_byte_length = 0
        self.flusher = None
        self.max_length = defaults['MAX_LINE_LENGTH']
        self.connection_retries = 5
        self.retry_backoff_factor = 0.5

        self.hostname = options.get('hostname', socket.gethostname())
        self.ip = options.get('ip', get_ip())
        self.mac = options.get('mac', None)
        self.level = options.get('level', 'info')
        self.verbose = str(options.get('verbose', 'true')).lower()
        self.app = options.get('app', '')
        self.env = options.get('env', '')
        self.url = options.get('url', defaults['LOGDNA_URL'])
        self.request_timeout = options.get('request_timeout', defaults['DEFAULT_REQUEST_TIMEOUT'])
        self.include_standard_meta = options.get('include_standard_meta', False)
        self.index_meta = options.get('index_meta', False)
        self.flush_limit = options.get('flush_limit', defaults['FLUSH_BYTE_LIMIT'])
        self.flush_interval = options.get('flush_interval', defaults['FLUSH_INTERVAL'])
        self.tags = options.get('tags', [])

        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(',')]
        elif not isinstance(self.tags, list):
            self.tags = []


        self.setLevel(logging.DEBUG)
        self.lock = threading.RLock()

        self.session = requests.Session()
        retry = Retry(connect=self.connection_retries, backoff_factor=self.retry_backoff_factor)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)

    def buffer_log(self, message):
        if message and message['line']:
            if len(message['line']) > self.max_length:
                message['line'] = message['line'][:self.max_length] + ' (cut off, too long...)'
                if self.verbose in ['true', 'debug', 'd']:
                    logger.debug('Line was longer than %s chars and was truncated.', str(self.max_length))

        self.buf_byte_length += sys.getsizeof(message)

        # Attempt to acquire lock to write to buf, otherwise write to secondary as flush occurs
        if not self.lock.acquire(blocking=False):
            self.secondary.append(message)
        else:
            self.buf.append(message)
            self.lock.release()
            if self.buf_byte_length >= self.flush_limit:
                self.flush()
                return

        if not self.flusher:
            self.flusher = threading.Timer(self.flush_interval, self.flush)
            self.flusher.start()

    def flush(self):
        if not self.buf or len(self.buf) < 0:
            return
        data = {'e': 'ls', 'ls': self.buf}
        try:
            # Ensure we have the lock when flushing
            if not self.lock.acquire(blocking=False):
                if not self.flusher:
                    self.flusher = threading.Timer(1, self.flush)
                    self.flusher.start()
            else:
                self.session.post(
                    url=self.url,
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
                self.buf_byte_length = 0
                if self.flusher:
                    self.flusher.cancel()
                    self.flusher = None
                self.lock.release()
                # Ensure messages that could've dropped are appended back onto buf
                self.buf = self.buf + self.secondary
                self.secondary = []
        except requests.exceptions.RequestException as e:
            if self.flusher:
                self.flusher.cancel()
                self.flusher = None
            self.lock.release()
            if not self.exception_flag:
                self.exception_flag = True
                if self.verbose in ['true', 'error', 'err', 'e']:
                    logger.error('Error in Request to LogDNA: %s', str(e))
        else:
            # when no RequestException happened
            self.exception_flag = False

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
                    message['meta'] = sanitize_meta(opts['meta'])
                else:
                    message['meta'] = json.dumps(opts['meta'])

        self.buffer_log(message)

    def close(self):
        """
        Close the log handler.

        Make sure that the log handler has attempted to flush the log buffer before closing.
        """
        try:
            self.flush()
        finally:
            logging.Handler.close(self)
