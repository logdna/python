import json
import logging
import requests
import socket
import sys
import threading
import time
from functools import reduce

from .configs import defaults
from .utils import sanitize_meta, get_ip


class LogDNAHandler(logging.Handler):
    def __init__(self, key, options={}):
        logging.Handler.__init__(self)
        self.internal_handler = logging.StreamHandler(sys.stdout)
        self.internal_handler.setLevel(logging.DEBUG)
        self.internalLogger = logging.getLogger('internal')
        self.internalLogger.setLevel(logging.DEBUG)
        self.internalLogger.addHandler(self.internal_handler)

        self.key = key
        self.buf = []
        self.secondary = []
        self.exception_flag = False
        self.flusher = None
        self.max_length = defaults['MAX_LINE_LENGTH']

        self.hostname = options.get('hostname', socket.gethostname())
        self.ip = options.get('ip', get_ip())
        self.mac = options.get('mac', None)
        self.level = options.get('level', 'info')
        self.verbose = str(options.get('verbose', 'true')).lower()
        self.app = options.get('app', '')
        self.env = options.get('env', '')
        self.url = options.get('url', defaults['LOGDNA_URL'])
        self.request_timeout = options.get('request_timeout',
                                           defaults['DEFAULT_REQUEST_TIMEOUT'])
        self.include_standard_meta = options.get('include_standard_meta',
                                                 False)
        self.index_meta = options.get('index_meta', False)
        self.flush_limit = options.get('flush_limit',
                                       defaults['FLUSH_BYTE_LIMIT'])
        self.flush_interval_secs = options.get('flush_interval',
                                               defaults['FLUSH_INTERVAL_SECS'])
        self.retry_interval_secs = options.get('retry_interval_secs',
                                               defaults['RETRY_INTERVAL_SECS'])
        self.tags = options.get('tags', [])
        self.buf_retention_byte_limit = options.get(
            'buf_retention_limit', defaults['BUF_RETENTION_BYTE_LIMIT'])
        self.user_agent = options.get('user_agent', defaults['USER_AGENT'])

        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(',')]
        elif not isinstance(self.tags, list):
            self.tags = []
        self.setLevel(logging.DEBUG)
        self.lock = threading.RLock()

    # TODO(esatterwhite): complexity too high (8)
    def buffer_log(self, message):
        if message and message['line']:
            if len(message['line']) > self.max_length:
                message['line'] = message[
                    'line'][:self.max_length] + ' (cut off, too long...)'
                if self.verbose in ['true', 'debug', 'd']:
                    self.internalLogger.debug(
                        'Line was longer than %s chars and was truncated.',
                        self.max_length)

        # Attempt to acquire lock to write to buf
        # otherwise write to secondary as flush occurs
        if self.lock.acquire(blocking=False):
            buf_size = reduce(lambda x, y: x + len(y['line']), self.buf, 0)

            if buf_size + len(message['line']) < self.buf_retention_byte_limit:
                self.buf.append(message)
            else:
                self.internalLogger.debug(
                    'The buffer size exceeded the limit: %s',
                    self.buf_retention_byte_limit)
            self.lock.release()

            if buf_size >= self.flush_limit and not self.exception_flag:
                self.flush()
        else:
            self.secondary.append(message)

        if not self.flusher:
            interval = (self.retry_interval_secs
                        if self.exception_flag else self.flush_interval_secs)
            self.flusher = threading.Timer(interval, self.flush)
            self.flusher.start()

    def clean_after_success(self):
        del self.buf[:]
        self.exception_flag = False
        if self.flusher:
            self.flusher.cancel()
            self.flusher = None

    def handle_exception(self, exception):
        if self.flusher:
            self.flusher.cancel()
            self.flusher = None
        self.exception_flag = True
        if self.verbose in ['true', 'error', 'err', 'e']:
            self.internalLogger.debug('Error sending logs %s', exception)

    # do not call without acquiring the lock
    def send_request(self):
        self.buf.extend(self.secondary)
        self.secondary = []
        data = {'e': 'ls', 'ls': self.buf}
        try:
            res = requests.post(url=self.url,
                                json=data,
                                auth=('user', self.key),
                                params={
                                    'hostname': self.hostname,
                                    'ip': self.ip,
                                    'mac': self.mac if self.mac else None,
                                    'tags': self.tags if self.tags else None
                                },
                                stream=True,
                                timeout=self.request_timeout,
                                headers={'user-agent': self.user_agent})
            res.raise_for_status()
            # when no RequestException happened
            self.clean_after_success()
        except requests.exceptions.RequestException as e:
            self.handle_exception(e)

    def flush(self):
        if len(self.buf) == 0:
            return
        if self.lock.acquire(blocking=False):
            self.send_request()
            self.lock.release()
        else:
            if not self.flusher:
                self.flusher = threading.Timer(1, self.flush)
                self.flusher.start()

    # TODO(esatterwhite): complexity too high (14)
    def emit(self, record):  # noqa: C901
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
        if len(self.buf) > 0:
            self.flush()
        logging.Handler.close(self)
