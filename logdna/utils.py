import json
import socket


def is_jsonable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError, ValueError):
        return False


def sanitize_meta(meta):
    keys_to_sanitize = []
    for key, value in meta.items():
        if not is_jsonable(value):
            keys_to_sanitize.append(key)
    if keys_to_sanitize:
        for key in keys_to_sanitize:
            del meta[key]
        meta['__errors'] = 'These keys have been sanitized: ' + ', '.join(
            keys_to_sanitize)
    return meta


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
