import logging
import os
from logdna import LogDNAHandler

app = os.environ.get('APP', 'bloop')
# Set your key as an env variable
# then import here, its best not to
# hard code your key!
key = '50193c701e25003b9e40124015bf2c2d'

log = logging.getLogger('logdna')
log.setLevel(logging.INFO)

options = {
  'hostname': 'pytest',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE',
  'url': 'https://logs.use.dev.logdna.net/logs/ingest'
}

# Defaults to False; when True meta objects are searchable
options['index_meta'] = True

test = LogDNAHandler(key, options)

log.addHandler(test)

log.warning("Warning message", {'app': app})
log.info("Info message", {'app': app})
