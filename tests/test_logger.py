import logging
import unittest
import requests
import time
import os

from logdna import LogDNAHandler
from concurrent.futures import ThreadPoolExecutor
from logdna.configs import defaults
from unittest import mock
from unittest.mock import patch

now = int(time.time())
expectedLines = []
LOGDNA_API_KEY = os.environ.get('LOGDNA_INGESTION_KEY')
logger = logging.getLogger('logdna')
logger.setLevel(logging.INFO)
sample_args = {
    'app': 'differentTest',
    'level': 'debug',
    'hostname': 'differentHost',
    'env': 'differentEnv'
}

sample_record = logging.LogRecord('test', logging.INFO, 'test', 5,
                                  'Something to test', [sample_args], '', '',
                                  '')
sample_message = {
    'line': 'Something to test',
    'hostname': 'differentHost',
    'level': 'debug',
    'app': 'differentTest',
    'env': 'differentEnv',
    'meta': {
        'args': sample_args,
        'name': 'test',
        'pathname': 'test',
        'lineno': 5
    }
}

sample_options = {
    'hostname': 'localhost',
    'ip': '10.0.1.1',
    'mac': 'C0:FF:EE:C0:FF:EE',
    'tags': 'sample,test',
    'index_meta': True,
    'now': int(time.time() * 1000),
    'retry_interval_secs': 0.5
}


class MockThreadPoolExecutor():
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def submit(self, fn, *args, **kwargs):
        # execute functions in series without creating threads
        # for easier unit testing
        result = fn(*args, **kwargs)
        return result

    def shutdown(self, wait=True):
        pass


class LogDNAHandlerTest(unittest.TestCase):

    def test_handler(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        self.assertIsInstance(handler, logging.Handler)
        self.assertIsInstance(handler.internal_handler, logging.StreamHandler)
        self.assertIsNotNone(handler.internalLogger)
        self.assertEqual(handler.key, LOGDNA_API_KEY)
        self.assertEqual(handler.hostname, sample_options['hostname'])
        self.assertEqual(handler.ip, sample_options['ip'])
        self.assertEqual(handler.mac, sample_options['mac'])
        self.assertEqual(handler.loglevel, 'info')
        self.assertEqual(handler.app, '')
        self.assertEqual(handler.env, '')
        self.assertEqual(handler.tags, sample_options['tags'].split(','))
        self.assertEqual(handler.custom_fields, defaults['META_FIELDS'])

        # Set the Connection Variables
        self.assertEqual(handler.url, defaults['LOGDNA_URL'])
        self.assertEqual(handler.request_timeout,
                         defaults['DEFAULT_REQUEST_TIMEOUT'])
        self.assertEqual(handler.user_agent, defaults['USER_AGENT'])
        self.assertEqual(handler.max_retry_attempts,
                         defaults['MAX_RETRY_ATTEMPTS'])
        self.assertEqual(handler.max_retry_jitter,
                         defaults['MAX_RETRY_JITTER'])
        self.assertEqual(handler.max_concurrent_requests,
                         defaults['MAX_CONCURRENT_REQUESTS'])
        self.assertEqual(handler.retry_interval_secs,
                         sample_options['retry_interval_secs'])

        # Set the Flush-related Variables
        self.assertEqual(handler.buf, [])
        self.assertEqual(handler.buf_size, 0)
        self.assertEqual(handler.secondary, [])
        self.assertFalse(handler.exception_flag)
        self.assertIsNone(handler.flusher)
        self.assertTrue(handler.index_meta)
        self.assertEqual(handler.flush_limit, defaults['FLUSH_LIMIT'])
        self.assertEqual(handler.flush_interval_secs,
                         defaults['FLUSH_INTERVAL_SECS'])
        self.assertEqual(handler.buf_retention_limit,
                         defaults['BUF_RETENTION_LIMIT'])

        # Set up the Thread Pools
        self.assertIsInstance(handler.worker_thread_pool, ThreadPoolExecutor)
        self.assertIsInstance(handler.request_thread_pool, ThreadPoolExecutor)
        self.assertEqual(handler.level, logging.DEBUG)

    def test_flusher(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        self.assertIsNone(handler.flusher)
        handler.start_flusher()
        self.assertIsNotNone(handler.flusher)
        handler.close_flusher()
        self.assertIsNone(handler.flusher)

    def test_emit(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        handler.buffer_log = unittest.mock.Mock()
        handler.emit(sample_record)
        sample_message['timestamp'] = unittest.mock.ANY
        handler.buffer_log.assert_called_once_with(sample_message)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 200
            r.reason = 'OK'
            post_mock.return_value = r
            handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
            sample_message['timestamp'] = unittest.mock.ANY
            handler.buf = [sample_message]
            handler.try_request()
            post_mock.assert_called_with(
                url=handler.url,
                json={
                    'e': 'ls',
                    'ls': handler.buf
                },
                auth=('user', handler.key),
                params={
                    'hostname': handler.hostname,
                    'ip': handler.ip,
                    'mac': handler.mac,
                    'tags': handler.tags,
                    'now': int(now * 1000)
                },
                stream=True,
                allow_redirects=True,
                timeout=handler.request_timeout,
                headers={'user-agent': handler.user_agent})
            self.assertFalse(handler.exception_flag)
            self.assertTrue(post_mock.call_count, 1)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_500(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 500
            r.reason = 'OK'
            post_mock.return_value = r
            handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
            sample_message['timestamp'] = unittest.mock.ANY
            handler.buf = [sample_message]
            handler.try_request()
            self.assertTrue(handler.exception_flag)
            self.assertTrue(post_mock.call_count, 3)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_403(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 403
            r.reason = 'OK'
            post_mock.return_value = r
            handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
            sample_message['timestamp'] = unittest.mock.ANY
            handler.buf = [sample_message]
            handler.try_request()
            self.assertFalse(handler.exception_flag)
            self.assertTrue(post_mock.call_count, 1)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_403_log_response(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 403
            r.reason = 'OK'
            post_mock.return_value = r
            sample_options['log_error_response'] = True
            handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
            sample_message['timestamp'] = unittest.mock.ANY
            handler.buf = [sample_message]
            handler.try_request()
            self.assertFalse(handler.exception_flag)
            self.assertTrue(post_mock.call_count, 1)

    def test_close(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        handler.close_flusher = unittest.mock.Mock()
        handler.flush_sync = unittest.mock.Mock()
        handler.close()
        handler.close_flusher.assert_called_once_with()
        handler.flush_sync.assert_called_once_with()
        self.assertIsNone(handler.worker_thread_pool)
        self.assertIsNone(handler.request_thread_pool)

    def test_flush(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        handler.worker_thread_pool = MockThreadPoolExecutor()
        handler.request_thread_pool = MockThreadPoolExecutor()
        handler.buf_size += 1
        handler.try_request = unittest.mock.Mock()
        handler.flush()
        handler.try_request.assert_called_once_with()

    def test_flush_secondary(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        clean = handler.clean_after_success
        handler.worker_thread_pool = MockThreadPoolExecutor()
        handler.request_thread_pool = MockThreadPoolExecutor()
        handler.buf_size = 0
        handler.secondary.append(sample_message)
        handler.send_request = unittest.mock.MagicMock(return_value=True)
        handler.clean_after_success = unittest.mock.Mock()
        self.assertEqual(handler.secondary, [sample_message])
        handler.flush()
        handler.send_request.assert_called_with({
            'e': 'ls',
            'ls': [sample_message]
        })
        clean()
        self.assertEqual(handler.secondary, [])
        self.assertEqual(handler.buf, [])

    def test_buffer_log(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        handler.worker_thread_pool = MockThreadPoolExecutor()
        handler.request_thread_pool = MockThreadPoolExecutor()
        handler.close_flusher = unittest.mock.Mock()
        handler.flush = unittest.mock.Mock()
        sample_message['timestamp'] = unittest.mock.ANY
        handler.flush_limit = 0
        handler.buffer_log(sample_message)
        handler.close_flusher.assert_called_once_with()
        handler.flush.assert_called_once_with()
        self.assertEqual(handler.buf, [sample_message])
        self.assertEqual(handler.buf_size, len(sample_message['line']))


if __name__ == '__main__':
    unittest.main()
