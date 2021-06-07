from os import path, sep

with open("{p}{s}VERSION".format(p=path.abspath(path.dirname(__file__)),
                                 s=sep)) as f:
    version = f.read().strip('\n')

defaults = {
    'DEFAULT_REQUEST_TIMEOUT': 30,
    'FLUSH_INTERVAL': 250,
    'FLUSH_LIMIT': 5 * 1024 * 1024,
    'LOGDNA_URL': 'https://logs.logdna.com/logs/ingest',
    'BUF_RETENTION_LIMIT': 4 * 1024 * 1024,
    'RETRY_INTERVAL': 5000,
    'USER_AGENT': 'python/%s' % version
}
