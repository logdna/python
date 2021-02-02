import json
import unittest

from http.server import BaseHTTPRequestHandler
from logdna import LogDNAHandler
from .mock.server import get_port, start_server
from .mock.log import logger, info, LOGDNA_API_KEY

expectedLines = []


class SuccessfulRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)

        self.end_headers()
        body = json.loads(body)['ls']
        for keys in body:
            expectedLines.append(keys['line'])


class FailedRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        self.rfile.read(content_length)
        self.send_response(400)
        self.end_headers()


class LogDNAHandlerTest(unittest.TestCase):
    def server_recieves_messages(self):
        port = get_port()
        options = {
            'hostname': 'localhost',
            'url': 'http://localhost:{0}'.format(port),
            'ip': '10.0.1.1',
            'mac': 'C0:FF:EE:C0:FF:EE'
        }

        handler = LogDNAHandler(LOGDNA_API_KEY, options)
        logger.addHandler(handler)
        line = "python python python"

        server_thread = start_server(port, SuccessfulRequestHandler)
        logdna_thread = info(line)

        server_thread.join()
        logdna_thread.join()

        self.assertEqual(len(expectedLines), 1)
        self.assertIn(line, expectedLines)
        logger.removeHandler(handler)

    def messages_preserved_if_excp(self):
        port = get_port()
        options = {
            'hostname': 'localhost',
            'url': 'http://localhost:{0}'.format(port),
            'ip': '10.0.1.1',
            'mac': 'C0:FF:EE:C0:FF:EE'
        }

        handler = LogDNAHandler(LOGDNA_API_KEY, options)
        logger.addHandler(handler)
        line = "second test. server fails"

        server_thread = start_server(port, FailedRequestHandler)
        logdna_thread = info(line)

        server_thread.join()
        logdna_thread.join()

        self.assertEqual(len(handler.buf), 1)
        logger.removeHandler(handler)

    def stops_retention_when_buf_is_full(self):
        port = get_port()
        options = {
            'hostname': 'localhost',
            'url': 'http://localhost:{0}'.format(port),
            'ip': '10.0.1.1',
            'mac': 'C0:FF:EE:C0:FF:EE',
            'buf_retention_limit': 50,
            'equest_timeout': 10,
            'flush_interval': 1,
            'retry_interval_secs': 1
        }

        handler = LogDNAHandler(LOGDNA_API_KEY, options)
        logger.addHandler(handler)
        line = "when buffer grows bigger than we want"
        lineTwo = "when buffer grows bigger than we want. And more and more"

        server_thread = start_server(port, FailedRequestHandler)
        logdna_thread = info(line, lineTwo)

        server_thread.join()
        logdna_thread.join()

        self.assertEqual(len(handler.buf), 1)
        self.assertNotEqual(handler.buf[0]['line'], lineTwo)
        logger.removeHandler(handler)

    def test_run_tests(self):
        self.server_recieves_messages()
        self.messages_preserved_if_excp()
        self.stops_retention_when_buf_is_full()


if __name__ == '__main__':
    unittest.main()
