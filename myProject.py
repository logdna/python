import logging
from logdna import LogDNAHandler

key = 'ab37921179dccd5eb6ed9898b9ef8f54'

log = logging.getLogger('logdna')
log.setLevel(logging.INFO)

options = {
  'hostname': 'vilyapytest',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE'
}

test = LogDNAHandler(key, options)

log.addHandler(test)

log.warn("Despite all the admiration", {'app': 'bloop'})
log.info("Saint Francis preacing to the birds")
