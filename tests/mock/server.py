import socket
from http.server import HTTPServer
from threading import Thread


def get_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    _, port = s.getsockname()
    s.close()
    return port


def start_server(port, cls):
    server = HTTPServer(('localhost', port), cls)
    thread = Thread(target=server.handle_request)
    thread.setDaemon(True)
    thread.start()
    return thread
