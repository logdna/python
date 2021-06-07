import json
import logging
import requests
import socket
import sys
import threading
import time

from concurrent.futures import ThreadPoolExecutor

from .configs import defaults
from .utils import sanitize_meta, get_ip


class LogDNAHandler(logging.Handler):
    def __init__(self, key, options={}):
        # Setup Handler
        logging.Handler.__init__(self)

        # Set Internal Logger
        self.internal_handler = logging.StreamHandler(sys.stdout)
        self.internal_handler.setLevel(logging.DEBUG)
        self.internalLogger = logging.getLogger('internal')
        self.internalLogger.addHandler(self.internal_handler)
        self.internalLogger.setLevel(logging.DEBUG)

        # Set the Custom Variables
        self.key = key
        self.hostname = options.get('hostname', socket.gethostname())
        self.ip = options.get('ip', get_ip())
        self.mac = options.get('mac', None)
        self.level = options.get('level', 'info')
        self.app = options.get('app', '')
        self.env = options.get('env', '')
        self.tags = options.get('tags', [])
        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(',')]
        elif not isinstance(self.tags, list):
            self.tags = []

        # Set the Connection Variables
        self.url = options.get('url', defaults['LOGDNA_URL'])
        self.request_timeout = options.get('request_timeout',
                                           defaults['DEFAULT_REQUEST_TIMEOUT'])
        self.user_agent = options.get('user_agent', defaults['USER_AGENT'])
        self.max_retry_attempts = options.get('max_retry_attempts',
                                              defaults['MAX_RETRY_ATTEMPTS'])
        self.max_retry_jitter = options.get('max_retry_jitter',
                                            defaults['MAX_RETRY_JITTER'])
        self.max_concurrent_requests = options.get(
            'max_concurrent_requests', defaults['MAX_CONCURRENT_REQUESTS'])
        self.retry_interval = options.get('retry_interval',
                                          defaults['RETRY_INTERVAL'])

        # Set the Flush-related Variables
        self.buf = []
        self.buf_size = 0
        self.secondary = []
        self.exception_flag = False
        self.flusher = None
        self.include_standard_meta = options.get('include_standard_meta',
                                                 False)
        self.index_meta = options.get('index_meta', False)
        self.flush_limit = options.get('flush_limit', defaults['FLUSH_LIMIT'])
        self.flush_interval = options.get('flush_interval',
                                          defaults['FLUSH_INTERVAL'])
        self.buf_retention_limit = options.get('buf_retention_limit',
                                               defaults['BUF_RETENTION_LIMIT'])

        # Set up the Thread Pools
        self.worker_thread_pool = ThreadPoolExecutor()
        self.request_thread_pool = ThreadPoolExecutor(
            max_workers=self.max_concurrent_requests)

        self.setLevel(logging.DEBUG)
        self.lock = threading.RLock()

    def start_flusher(self):
        if not self.flusher:
            interval = (self.retry_interval
                        if self.exception_flag else self.flush_interval)
            self.flusher = threading.Timer(float(interval / 1000), self.flush)
            self.flusher.start()

    def close_flusher(self):
        if self.flusher:
            self.flusher.cancel()
            self.flusher = None

    def buffer_log(self, message):
        if self.worker_thread_pool:
            try:
                self.worker_thread_pool.submit(self.buffer_log_sync, message)
            except RuntimeError:
                self.buffer_log_sync(message)
            except Exception as e:
                self.internalLogger.debug('Error in calling buffer_log: %s', e)

    def buffer_log_sync(self, message):
        # Attempt to acquire lock to write to buf
        # otherwise write to secondary as flush occurs
        if self.lock.acquire(blocking=False):
            msglen = len(message['line'])
            if self.buf_size + msglen < self.buf_retention_limit:
                self.buf.append(message)
                self.buf_size += msglen
            else:
                self.internalLogger.debug(
                    'The buffer size exceeded the limit: %s',
                    self.buf_retention_limit)
            self.lock.release()

            if self.buf_size >= self.flush_limit and not self.exception_flag:
                self.close_flusher()
                self.flush()
            else:
                self.start_flusher()
        else:
            self.secondary.append(message)

    def clean_after_success(self):
        del self.buf[:]
        self.buf_size = 0
        self.exception_flag = False
        self.close_flusher()

    def flush(self):
        if self.worker_thread_pool:
            try:
                self.worker_thread_pool.submit(self.flush_sync)
            except RuntimeError:
                self.flush_sync()
            except Exception as e:
                self.internalLogger.debug('Error in calling flush: %s', e)

    def flush_sync(self):
        if self.buf_size == 0:
            return
        if self.lock.acquire(blocking=False):
            if self.request_thread_pool:
                try:
                    self.request_thread_pool.submit(self.try_request)
                except RuntimeError:
                    self.try_request()
                except Exception as e:
                    self.internalLogger.debug(
                        'Error in calling try_request: %s', e)
            self.lock.release()
        else:
            self.start_flusher()

    def try_request(self):
        self.buf.extend(self.secondary)
        self.secondary = []
        data = {'e': 'ls', 'ls': self.buf}
        retries = 0
        while True:
            retries += 1
            if retries > self.max_retry_attempts:
                self.internalLogger.debug(
                    'Flush exceeded %s tries. Discarding flush buffer',
                    self.max_retry_attempts)
                self.close_flusher()
                self.exception_flag = True
                break

            if self.send_request(data):
                self.clean_after_success()
                break

            sleep_time = self.retry_interval * (1 << (retries - 1))
            sleep_time += self.max_retry_jitter
            time.sleep(sleep_time)

    def send_request(self, data):
        try:
            response = requests.post(url=self.url,
                                     json=data,
                                     auth=('user', self.key),
                                     params={
                                         'hostname': self.hostname,
                                         'ip': self.ip,
                                         'mac': self.mac,
                                         'tags': self.tags
                                     },
                                     stream=True,
                                     timeout=self.request_timeout,
                                     headers={'user-agent': self.user_agent})

            response.raise_for_status()
            status_code = response.status_code
            if status_code in [401, 403]:
                self.internalLogger.debug(
                    'Please provide a valid ingestion key.' +
                    ' Discarding flush buffer')
                return True

            if status_code == 200:
                return True

            if status_code in [400, 500, 504]:
                self.internalLogger.debug('The request failed %s. Retrying...',
                                          response.reason)
                return True
            else:
                self.internalLogger.debug(
                    'The request failed: %s. Retrying...', response.reason)

        except requests.exceptions.Timeout as timeout:
            self.internalLogger.debug('Timeout error occurred %s. Retrying...',
                                      timeout)

        except requests.exceptions.RequestException as exception:
            self.internalLogger.debug(
                'Error sending logs %s. Discarding flush buffer', exception)
            return True

        return False

    def emit(self, record):
        msg = self.format(record)
        record = record.__dict__
        message = {
            'hostname': self.hostname,
            'timestamp': int(time.time() * 1000),
            'line': msg,
            'level': record['levelname'] or self.level,
            'app': self.app or record['module'],
            'env': self.env
        }

        opts = {}
        if 'args' in record and not isinstance(record['args'], tuple):
            opts = record['args']

        for key in message.keys():
            if key in opts:
                message[key] = opts[key]

        if self.include_standard_meta:
            if 'meta' not in opts:
                opts['meta'] = {}
            for key in ['name', 'pathname', 'lineno']:
                if key in record:
                    opts['meta'][key] = record[key]
            if self.index_meta:
                message['meta'] = sanitize_meta(opts['meta'])
            else:
                message['meta'] = json.dumps(opts['meta'])

        self.buffer_log(message)

    def close(self):
        self.close_flusher()
        self.flush_sync()
        if self.worker_thread_pool:
            self.worker_thread_pool.shutdown(wait=True)
            self.worker_thread_pool = None
        if self.request_thread_pool:
            self.request_thread_pool.shutdown(wait=True)
            self.request_thread_pool = None
        logging.Handler.close(self)
