from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import logging
import threading
from logdna import LogDNAHandler
import unittest
import json
import concurrent.futures
import time


'''
For now I suggest running the test methods separatley by commenting out
all except one. This will gourantee the test correctness.
'''
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
    def test_serverRecievesMessages(self):
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

        self.assertTrue(len(expectedLines) == 1)
        self.assertTrue(len(test.buf) == 0)
        self.assertTrue(line in expectedLines)


    def test_messagesPreservedIfExcp(self):
        server_address = ('localhost', 8081)

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

        self.assertTrue(len(failedCaseLogger.buf) == 1)


if __name__ == '__main__':
    unittest.main()
