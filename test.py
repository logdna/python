'''
    An example of how to use the LogDNA Handler
'''

import logging
import timeit
import sys

from logdna import LogDNAHandler

# from guppy import hpy
# h = hpy()

key = 'YOUR API KEY HERE'
log = logging.getLogger('logdna')
log.setLevel(logging.INFO)
test = LogDNAHandler(key, { 'hostname': 'pytest' })

log.addHandler(test)

log.warn("Warning message", {'app': 'bloop'})
log.info("Info message")
# print h.heap()

# Lines will be in order upon refresh
def timeThis():
    for x in range(100):
        log.info('DINGLEBOP ' + str(x))

print (timeit.timeit(timeThis, number=2))

# print h.heap()
