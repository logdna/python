import logging
import requests
import socket
import sys
import threading
import time

from concurrent.futures import ThreadPoolExecutor

from .configs import defaults
from .utils import sanitize_meta, get_ip, normalize_list_option


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
        self.loglevel = options.get('level', 'info')
        self.app = options.get('app', '')
        self.env = options.get('env', '')
        self.tags = normalize_list_option(options, 'tags')
        self.custom_fields = normalize_list_option(options, 'custom_fields')
        self.custom_fields += defaults['META_FIELDS']
        self.log_error_response = options.get('log_error_response', False)

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
        self.retry_interval_secs = options.get('retry_interval_secs',
                                               defaults['RETRY_INTERVAL_SECS'])

        # Set the Flush-related Variables
        self.buf = []
        self.buf_size = 0
        self.secondary = []
        self.exception_flag = False
        self.flusher = None
        self.include_standard_meta = options.get('include_standard_meta', None)

        if self.include_standard_meta is not None:
            self.internalLogger.debug(
                '"include_standard_meta" option will be deprecated ' +
                'removed in the upcoming major release')

        self.index_meta = options.get('index_meta', False)
        self.flush_limit = options.get('flush_limit', defaults['FLUSH_LIMIT'])
        self.flush_interval_secs = options.get('flush_interval',
                                               defaults['FLUSH_INTERVAL_SECS'])
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
            self.flusher = threading.Timer(self.flush_interval_secs,
                                           self.flush)
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

            if self.buf_size >= self.flush_limit and not self.exception_flag:
                self.close_flusher()
                self.flush()
            else:
                self.start_flusher()
            self.lock.release()
        else:
            self.secondary.append(message)

    def clean_after_success(self):
        self.close_flusher()
        self.buf.clear()
        self.buf_size = 0
        self.exception_flag = False

    def flush(self):
        if self.worker_thread_pool:
            try:
                self.worker_thread_pool.submit(self.flush_sync)
            except RuntimeError:
                self.flush_sync()
            except Exception as e:
                self.internalLogger.debug('Error in calling flush: %s', e)

    def flush_sync(self):
        if self.buf_size == 0 and len(self.secondary) == 0:
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
                finally:
                    self.lock.release()
            else:
                self.lock.release()
        else:
            self.close_flusher()
            self.start_flusher()

    def try_request(self):
        self.buf.extend(self.secondary)
        self.secondary = []
        data = {'e': 'ls', 'ls': self.buf}
        retries = 0
        while retries < self.max_retry_attempts:
            retries += 1
            if self.send_request(data):
                self.clean_after_success()
                break

            sleep_time = self.retry_interval_secs * (1 << (retries - 1))
            sleep_time += self.max_retry_jitter
            time.sleep(sleep_time)

        if retries >= self.max_retry_attempts:
            self.internalLogger.debug(
                'Flush exceeded %s tries. Discarding flush buffer',
                self.max_retry_attempts)
            self.close_flusher()
            self.exception_flag = True

    def send_request(self, data):  # noqa: max-complexity: 13
        """
            Send log data to LogDNA server
        Returns:
            True  - discard flush buffer
            False - retry, keep flush buffer
        """
        try:
            response = requests.post(url=self.url,
                                     json=data,
                                     auth=('user', self.key),
                                     params={
                                         'hostname': self.hostname,
                                         'ip': self.ip,
                                         'mac': self.mac,
                                         'tags': self.tags,
                                         'now': int(time.time() * 1000)
                                     },
                                     stream=True,
                                     allow_redirects=True,
                                     timeout=self.request_timeout,
                                     headers={'user-agent': self.user_agent})

            status_code = response.status_code
            '''
                response code:
                    1XX                       unexpected status
                    200                       expected status, OK
                    2XX                       unexpected status
                    301 302 303               unexpected status,
                                              per "allow_redirects=True"
                    3XX                       unexpected status
                    401, 403                  expected client error,
                                              invalid ingestion key
                    4XX                       unexpected client error
                    500 502 503 507           expected server error, transient
                    5XX                       unexpected server error
                handling:
                    expected status           discard flush buffer
                    unexpected status         log + discard flush buffer
                    expected client error     log + discard flush buffer
                    unexpected client error   log + discard flush buffer
                    expected server error     log + retry
                    unexpected server error   log + discard flush buffer
            '''
            if status_code == 200:
                return True  # discard

            if isinstance(response.reason, bytes):
                # We attempt to decode utf-8 first because some servers
                # choose to localize their reason strings. If the string
                # isn't utf-8, we fall back to iso-8859-1 for all other
                # encodings. (See PR #3538)
                try:
                    reason = response.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = response.reason.decode('iso-8859-1')
            else:
                reason = response.reason

            if 200 < status_code <= 399:
                self.internalLogger.debug('Unexpected response: %s. ' +
                                          'Discarding flush buffer',
                                          reason)
                if self.log_error_response:
                    self.internalLogger.debug(
                        'Error Response: %s', response.text)
                return True  # discard

            if status_code in [401, 403]:
                self.internalLogger.debug(
                    'Please provide a valid ingestion key. ' +
                    'Discarding flush buffer')
                if self.log_error_response:
                    self.internalLogger.debug(
                        'Error Response: %s', response.text)
                return True  # discard

            if 400 <= status_code <= 499:
                self.internalLogger.debug('Client Error: %s. ' +
                                          'Discarding flush buffer',
                                          reason)
                if self.log_error_response:
                    self.internalLogger.debug(
                        'Error Response: %s', response.text)
                return True  # discard

            if status_code in [500, 502, 503, 507]:
                self.internalLogger.debug('Server Error: %s. Retrying...',
                                          reason)
                if self.log_error_response:
                    self.internalLogger.debug(
                        'Error Response: %s', response.text)
                return False  # retry

            self.internalLogger.debug('The request failed: %s.' +
                                      'Discarding flush buffer',
                                      reason)

        except requests.exceptions.Timeout as timeout:
            self.internalLogger.debug('Timeout Error: %s. Retrying...',
                                      timeout)
            return False  # retry

        except requests.exceptions.RequestException as exception:
            self.internalLogger.debug(
                'Error sending logs %s. Discarding flush buffer', exception)

        return True  # discard

    def emit(self, record):
        msg = self.format(record)
        record = record.__dict__
        message = {
            'hostname': self.hostname,
            'timestamp': int(time.time() * 1000),
            'line': msg,
            'level': record['levelname'] or self.loglevel,
            'app': self.app or record['module'],
            'env': self.env
        }

        message['meta'] = {}
        for key in self.custom_fields:
            if key in record:
                if isinstance(record[key], tuple):
                    message['meta'][key] = list(record[key])
                elif record[key] is not None:
                    message['meta'][key] = record[key]

        message['meta'] = sanitize_meta(message['meta'], self.index_meta)

        opts = {}
        if 'args' in record and not isinstance(record['args'], tuple):
            opts = record['args']

        for key in ['app', 'env', 'hostname', 'level', 'timestamp']:
            if key in opts:
                message[key] = opts[key]

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
