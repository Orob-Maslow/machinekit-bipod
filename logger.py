#!/usr/bin/python
import logging
from subprocess import Popen, PIPE
import requests

#todo - lockfile

# setup log
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

payload = { 'private_key': '87y0npg4jpt3xDgLz9YqT5xrPbq' }

log.info("started")

# define HAL stuff to log
pins = [
    { 'pin' : 'xbee.gond_batt', 'tag': 'pen_batt' },
    { 'pin' : 'xbee.gond_rx_count', 'tag': 'pen_rxcount' },
    { 'pin' : 'xbee.gond_err_count', 'tag': 'pen_errcount' },
    { 'pin' : 'xbee.cksum-err', 'tag': 'xbee_cksumerr' },
    { 'pin' : 'xbee.rx-err', 'tag': 'xbee_rxerr' },
    ]

# fetch robot data from the HAL
for pin in pins:
    p = Popen('halcmd getp %s' % pin['pin'], shell=True, stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    log.debug("error code = %d" % p.returncode)
    log.debug("stderr = %s" % err)
    log.debug("stdout = %s" % stdout)

    payload[pin['tag']] = stdout

# get uptime
with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    payload["uptime"] = uptime_seconds

# get linuxcnc stats
import linuxcnc
sta = linuxcnc.stat()
sta.poll()
payload['cnc_execstate'] = sta.exec_state
payload['cnc_interpstate'] = sta.interp_state
payload['cnc_state'] = sta.state
payload['xpos'] = sta.position[0]
payload['ypos'] = sta.position[1]
payload['zpos'] = sta.position[2]

# log it
log.info("logging to phant")
url = 'http://phant.cursivedata.co.uk/input/L4y9DEbMzEUOdzPYlQ9NSJAXom4'
r = requests.get(url, params=payload)
log.debug("get status = %d" % r.status_code)

log.info("finished")
