import logging
import unittest

from logdna import LogDNAHandler
from concurrent.futures import ThreadPoolExecutor
from logdna.configs import defaults

expectedLines = []
LOGDNA_API_KEY = '< YOUR INGESTION KEY HERE >'
logger = logging.getLogger('logdna')
logger.setLevel(logging.INFO)


class LogDNAHandlerTest(unittest.TestCase):
    def handler_test(self):
        options = {
            'hostname': 'localhost',
            'ip': '10.0.1.1',
            'mac': 'C0:FF:EE:C0:FF:EE',
            'tags': 'sample,test'
        }

        handler = LogDNAHandler(LOGDNA_API_KEY, options)
        self.assertIsInstance(handler, logging.Handler)
        self.assertIsInstance(handler.internal_handler, logging.StreamHandler)
        self.assertIsNotNone(handler.internalLogger)
        self.assertEqual(handler.key, LOGDNA_API_KEY)
        self.assertEqual(handler.hostname, options['hostname'])
        self.assertEqual(handler.ip, options['ip'])
        self.assertEqual(handler.mac, options['mac'])
        self.assertEqual(handler.loglevel, 'info')
        self.assertEqual(handler.app, '')
        self.assertEqual(handler.env, '')
        self.assertEqual(handler.tags, options['tags'].split(','))

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
                         defaults['RETRY_INTERVAL_SECS'])

        # Set the Flush-related Variables
        self.assertEqual(handler.buf, [])
        self.assertEqual(handler.buf_size, 0)
        self.assertEqual(handler.secondary, [])
        self.assertFalse(handler.exception_flag)
        self.assertIsNone(handler.flusher)
        self.assertFalse(handler.include_standard_meta)
        self.assertFalse(handler.index_meta)
        self.assertEqual(handler.flush_limit, defaults['FLUSH_LIMIT'])
        self.assertEqual(handler.flush_interval_secs,
                         defaults['FLUSH_INTERVAL_SECS'])
        self.assertEqual(handler.buf_retention_limit,
                         defaults['BUF_RETENTION_LIMIT'])

        # Set up the Thread Pools
        self.assertIsInstance(handler.worker_thread_pool, ThreadPoolExecutor)
        self.assertIsInstance(handler.request_thread_pool, ThreadPoolExecutor)
        self.assertEqual(handler.level, logging.DEBUG)

    def flusher_test(self):
        options = {
            'hostname': 'localhost',
            'ip': '10.0.1.1',
            'mac': 'C0:FF:EE:C0:FF:EE',
            'tags': 'sample,test'
        }

        handler = LogDNAHandler(LOGDNA_API_KEY, options)
        self.assertIsNone(handler.flusher)
        handler.start_flusher()
        self.assertIsNotNone(handler.flusher)
        handler.close_flusher()
        self.assertIsNone(handler.flusher)

    def test_run_tests(self):
        self.handler_test()
        self.flusher_test()


if __name__ == '__main__':
    unittest.main()
