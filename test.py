'''
    An example of how to use the LogDNA Handler
'''

import logging
import timeit
import sys
import time

from logdna.logdna import LogDNAHandler

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
    for x in range(7):
        log.info('GORPGORP ' + str(x))
        #log.info('%s before you %s', 'Look', 'Leap')

def main_loop():
    while 1:
        print (timeit.timeit(timeThis, number=2))
        time.sleep(10)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)

# print h.heap()
