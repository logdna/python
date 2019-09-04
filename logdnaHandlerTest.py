import concurrent.futures
import json
import threading
import time

from http.server import BaseHTTPRequestHandler,HTTPServer
import logging
import unittest

from logdna import LogDNAHandler

current_milli_time = lambda: int(round(time.time() * 1000))

key = '< YOUR INGESTION KEY HERE >'
log = logging.getLogger('logdna')
log.setLevel(logging.INFO)

options = {
  'hostname': 'localhost',
  'url': 'http://localhost:8081',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE'
}

expectedLines = []
class successful_RequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)

        self.end_headers()
        body = json.loads(body)['ls']
        for keys in body:
            expectedLines.append(keys['line'])

class failed_RequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(400)
        self.end_headers()

class LogDNAHandlerTest(unittest.TestCase):
    def server_recieves_messages(self):
        options = {
          'hostname': 'localhost',
          'url': 'http://localhost:8081',
          'ip': '10.0.1.1',
          'mac': 'C0:FF:EE:C0:FF:EE'
        }

        successRes = True
        server_address = ('localhost', 8081)
        httpd = HTTPServer(server_address, successful_RequestHandler)

        test = LogDNAHandler(key, options)
        log.addHandler(test)
        line = "python python python"

        def send_log():
            log.info(line)

        serverThread = threading.Thread(target=httpd.handle_request)
        logdnaThread = threading.Thread(target=send_log)
        serverThread.daemon = True
        logdnaThread.daemon = True

        serverThread.start()
        logdnaThread.start()

        serverThread.join()
        logdnaThread.join()

        self.assertEqual(len(expectedLines), 1)
        self.assertIn(line, expectedLines)

    def messages_preserved_if_excp(self):
        options = {
          'hostname': 'localhost',
          'url': 'http://localhost:8080',
          'ip': '10.0.1.1',
          'mac': 'C0:FF:EE:C0:FF:EE'
        }
        server_address = ('localhost', 8080)
        httpd = HTTPServer(server_address, failed_RequestHandler)

        failedCaseLogger = LogDNAHandler(key, options)
        log.addHandler(failedCaseLogger)
        line = "second test. server fails"

        def send_log_to_fail():
            log.info(line)

        serverThread = threading.Thread(target=httpd.handle_request)
        logdnaThread = threading.Thread(target=send_log_to_fail)
        serverThread.daemon = True
        logdnaThread.daemon = True

        serverThread.start()
        logdnaThread.start()

        serverThread.join()
        logdnaThread.join()
        self.assertEqual(len(failedCaseLogger.buf), 1)


    def stops_retention_when_buf_is_full(self):
        options = {
          'hostname': 'localhost',
          'url': 'http://localhost:1337',
          'ip': '10.0.1.1',
          'mac': 'C0:FF:EE:C0:FF:EE',
          'buf_retention_limit': 50,
          'equest_timeout': 10,
          'flush_interval': 1,
          'retry_interval_secs': 1

        }
        server_address = ('localhost', 1337)

        httpd = HTTPServer(server_address, failed_RequestHandler)

        failedCaseLogger = LogDNAHandler(key, options)
        log.addHandler(failedCaseLogger)
        line = "when buffer grows bigger than we want"
        lineTwo = "when buffer grows bigger than we want. And more and more"

        def send_log_to_fail():
            log.info(line)
            log.info(lineTwo)


        serverThread = threading.Thread(target=httpd.handle_request)
        logdnaThread = threading.Thread(target=send_log_to_fail)
        serverThread.daemon = True
        logdnaThread.daemon = True

        serverThread.start()
        logdnaThread.start()

        serverThread.join()
        logdnaThread.join()

        self.assertEqual(len(failedCaseLogger.buf), 1)
        self.assertNotEqual(failedCaseLogger.buf[0]['line'], lineTwo)

    def test_run_tests(self):
        self.server_recieves_messages()
        self.messages_preserved_if_excp()
        self.stops_retention_when_buf_is_full()


if __name__ == '__main__':
    unittest.main()
