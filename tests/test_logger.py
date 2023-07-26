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
    def setUp(self):
        self.handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)

    def tearDown(self):
        self.handler.close()

    def test_handler(self):
        self.assertIsInstance(self.handler, logging.Handler)
        self.assertIsInstance(
            self.handler.internal_handler, logging.StreamHandler)
        self.assertIsNotNone(self.handler.internalLogger)
        self.assertEqual(self.handler.key, LOGDNA_API_KEY)
        self.assertEqual(self.handler.hostname, sample_options['hostname'])
        self.assertEqual(self.handler.ip, sample_options['ip'])
        self.assertEqual(self.handler.mac, sample_options['mac'])
        self.assertEqual(self.handler.loglevel, 'info')
        self.assertEqual(self.handler.app, '')
        self.assertEqual(self.handler.env, '')
        self.assertEqual(self.handler.tags, sample_options['tags'].split(','))
        self.assertEqual(self.handler.custom_fields, defaults['META_FIELDS'])

        # Set the Connection Variables
        self.assertEqual(self.handler.url, defaults['LOGDNA_URL'])
        self.assertEqual(self.handler.request_timeout,
                         defaults['DEFAULT_REQUEST_TIMEOUT'])
        self.assertEqual(self.handler.user_agent, defaults['USER_AGENT'])
        self.assertEqual(self.handler.max_retry_attempts,
                         defaults['MAX_RETRY_ATTEMPTS'])
        self.assertEqual(self.handler.max_retry_jitter,
                         defaults['MAX_RETRY_JITTER'])
        self.assertEqual(self.handler.max_concurrent_requests,
                         defaults['MAX_CONCURRENT_REQUESTS'])
        self.assertEqual(self.handler.retry_interval_secs,
                         sample_options['retry_interval_secs'])

        # Set the Flush-related Variables
        self.assertEqual(self.handler.buf, [])
        self.assertEqual(self.handler.buf_size, 0)
        self.assertIsNotNone(self.handler.flusher)
        self.assertTrue(self.handler.index_meta)
        self.assertEqual(self.handler.flush_limit, defaults['FLUSH_LIMIT'])
        self.assertEqual(self.handler.flush_interval_secs,
                         defaults['FLUSH_INTERVAL_SECS'])
        self.assertEqual(self.handler.buf_retention_limit,
                         defaults['BUF_RETENTION_LIMIT'])

        # Set up the Thread Pools
        self.assertIsInstance(
            self.handler.worker_thread_pool, ThreadPoolExecutor)
        self.assertIsInstance(
            self.handler.request_thread_pool, ThreadPoolExecutor)
        self.assertEqual(self.handler.level, logging.DEBUG)

    def test_flusher(self):
        self.assertIsNotNone(self.handler.flusher)
        self.handler.close_flusher()
        self.assertIsNone(self.handler.flusher)
        self.assertTrue(self.handler.flusher_stopped)

    def test_emit(self):
        self.handler.buffer_log = unittest.mock.Mock()
        self.handler.emit(sample_record)
        sample_message['timestamp'] = unittest.mock.ANY
        self.handler.buffer_log.assert_called_once_with(sample_message)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_lock_and_do_flush_request(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 200
            r.reason = 'OK'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            test_buf = self.handler.buf.copy()
            self.handler.try_lock_and_do_flush_request()
            post_mock.assert_called_with(
                url=self.handler.url,
                json={
                    'e': 'ls',
                    'ls': test_buf
                },
                params={
                    'hostname': self.handler.hostname,
                    'ip': self.handler.ip,
                    'mac': self.handler.mac,
                    'tags': self.handler.tags,
                    'now': int(now * 1000)
                },
                stream=True,
                allow_redirects=True,
                timeout=self.handler.request_timeout,
                headers={
                    'user-agent': self.handler.user_agent,
                    'apikey': LOGDNA_API_KEY})
            self.assertTrue(post_mock.call_count, 1)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_500(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 500
            r.reason = 'Internal Server Error'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 3)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_502(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 502
            r.reason = 'Bad Gateway'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 3)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_504(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 504
            r.reason = 'Gateway Timeout'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 3)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_429(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 429
            r.reason = 'Too Many Requests'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 3)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_403(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 403
            r.reason = 'Forbidden'
            post_mock.return_value = r
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 1)

    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_try_request_403_log_response(self):
        with patch('requests.post') as post_mock:
            r = requests.Response()
            r.status_code = 403
            r.reason = 'Forbidden'
            post_mock.return_value = r
            sample_options['log_error_response'] = True
            sample_message['timestamp'] = unittest.mock.ANY
            self.handler.buf = [sample_message]
            self.handler.try_request([])
            self.assertTrue(post_mock.call_count, 1)

    def test_close(self):
        close_flusher_mock = unittest.mock.Mock()
        close_flusher_mock.side_effect = self.handler.close_flusher
        self.handler.close_flusher = close_flusher_mock
        self.handler.schedule_flush_sync = unittest.mock.Mock()
        self.handler.close()
        self.handler.close_flusher.assert_called_once_with()
        self.handler.schedule_flush_sync.assert_called_once_with(
            should_block=True)
        self.assertIsNone(self.handler.worker_thread_pool)
        self.assertIsNone(self.handler.request_thread_pool)

    def test_flush(self):
        self.handler.worker_thread_pool = MockThreadPoolExecutor()
        self.handler.request_thread_pool = MockThreadPoolExecutor()
        self.handler.buf = [sample_message]
        self.handler.buf_size += len(self.handler.buf)
        self.handler.try_request = unittest.mock.Mock()
        self.handler.flush()
        self.handler.try_request.assert_called_once_with([sample_message])

    def test_buffer_log(self):
        self.handler.worker_thread_pool = MockThreadPoolExecutor()
        self.handler.request_thread_pool = MockThreadPoolExecutor()
        self.handler.flush = unittest.mock.Mock()
        sample_message['timestamp'] = unittest.mock.ANY
        self.handler.flush_limit = 0
        self.handler.buffer_log(sample_message)
        self.handler.flush.assert_called_once_with()
        self.assertEqual(self.handler.buf, [sample_message])
        self.assertEqual(self.handler.buf_size, len(sample_message['line']))

    # Attempts to reproduce the specific scenario that resulted in
    # https://mezmo.atlassian.net/browse/LOG-15414 where log messages
    # would be dropped due to race conditions. The test essentially
    # does the following:
    # 1. Create a LogDNAHandler
    # 2. Call handler.emit() with a large number of log records at a rate
    #    sufficiently high to trigger the race
    # 3. Verify that no log records are dropped.
    #
    # This test is not deterministic, but it should be sufficient to
    # catch regressions. It reliably reproduces the issue in question
    # and fails with the previous version of this code.
    @mock.patch('time.time', unittest.mock.MagicMock(return_value=now))
    def test_when_emitManyLogs_then_noLogsDropped(self):
        num_logs = 10**5
        received = list()

        def append_received(json=None, **kwargs):
            ids = [int(log['line']) for log in json['ls']]
            for id in ids:
                received.append(id)
            r = requests.Response()
            r.status_code = 200
            r.reason = 'OK'
            # Simulate some reasonable request latency
            time.sleep(0.1)
            return r

        def get_sample_record(id):
            return logging.LogRecord(
                name='test',
                level=logging.INFO,
                pathname='test',
                lineno=5,
                msg=str(id),
                args=[sample_args],
                exc_info='',
                func='',
                sinfo='')

        with patch('requests.post', side_effect=append_received):
            for i in range(num_logs):
                self.handler.emit(get_sample_record(i))
            self.handler.close()

        self.assertEqual(len(received), num_logs)
        self.assertEquals(set(received), set(range(num_logs)))

    def test_when_handlerShutDown_then_handlerDoesNotHang(self):
        handler = LogDNAHandler(LOGDNA_API_KEY, sample_options)
        self.assertIsNotNone(handler)
        # Do nothing. This test should pass by virtue of not hanging.


if __name__ == '__main__':
    unittest.main()
