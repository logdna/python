from os import path, sep

with open("{p}{s}VERSION".format(p=path.abspath(path.dirname(__file__)),
                                 s=sep)) as f:
    version = f.read().strip('\n')

defaults = {
    'DEFAULT_REQUEST_TIMEOUT': 30,
    'FLUSH_INTERVAL_SECS': 0.25,
    'FLUSH_LIMIT': 2 * 1024 * 1024,
    'MAX_CONCURRENT_REQUESTS': 10,
    'MAX_RETRY_ATTEMPTS': 3,
    'MAX_RETRY_JITTER': 0.5,
    'META_FIELDS': ['args', 'name', 'pathname', 'lineno'],
    'LOGDNA_URL': 'https://logs.logdna.com/logs/ingest',
    'BUF_RETENTION_LIMIT': 4 * 1024 * 1024,
    'RETRY_INTERVAL_SECS': 5,
    'USER_AGENT': 'python/%s' % version
}
