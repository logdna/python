with open('VERSION.txt') as version_file:
    pkg_version = version_file.read().strip()

defaults = {
    'DEFAULT_REQUEST_TIMEOUT': 30,
    'MAX_LINE_LENGTH': 32000,
    'FLUSH_INTERVAL_SECS': 5,
    'FLUSH_BYTE_LIMIT': 2 * 1024 * 1024,
    'LOGDNA_URL': 'https://logs.logdna.com/logs/ingest',
    'BUF_RETENTION_BYTE_LIMIT': 4 * 1024 * 1024,
    'RETRY_INTERVAL_SECS': 8,
    'LOGDNA_PKG_V': pkg_version
}
