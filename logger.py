#!/usr/bin/python
import logging
from subprocess import Popen, PIPE
import requests

log = logging.getLogger('')
log.setLevel(logging.DEBUG)

# create console handler and set level to info
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# create file handler and set to debug
fh = logging.FileHandler('logger.log')
fh.setFormatter(log_format)
log.addHandler(fh)

log.info("started")
pins = [
    { 'pin' : 'axis.0.motor-pos-cmd', 'tag': 'xpos' },
    { 'pin' : 'axis.1.motor-pos-cmd', 'tag': 'ypos' },
    { 'pin' : 'axis.2.motor-pos-cmd', 'tag': 'zpos' },
    { 'pin' : 'xbee.batt', 'tag': 'xbeebatt' },
    { 'pin' : 'xbee.cksum-err', 'tag': 'xbeecksumerr' },
    { 'pin' : 'xbee.no-rx-err', 'tag': 'xbeerxerr' },
    ]

payload = { 'private_key': '87y0npg4jpt3xDgLz9YqT5xrPbq' }
for pin in pins:
# fetch it
    p = Popen('halcmd getp %s' % pin['pin'], shell=True, stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    log.debug("error code = %d" % p.returncode)
    log.debug("stderr = %s" % err)
    log.debug("stdout = %s" % stdout)

    payload[pin['tag']] = stdout

# log it
log.info("logging to phant")
url = 'http://phant.cursivedata.co.uk/input/L4y9DEbMzEUOdzPYlQ9NSJAXom4'
r = requests.get(url, params=payload)
log.debug("get status = %d" % r.status_code)
log.info("finished")
