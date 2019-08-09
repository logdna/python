import logging
from logdna import LogDNAHandler

key = 'd8e14421399a44a9a35dfc49c7f5f0aa'

log = logging.getLogger('logdna')
log.setLevel(logging.INFO)

options = {
  'hostname': 'vilyapytest',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE'
}

test = LogDNAHandler(key, options)

log.addHandler(test)

log.warn("message message python python", {'app': 'bloop'})
log.info("python python python")
