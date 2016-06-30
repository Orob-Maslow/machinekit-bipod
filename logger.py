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

# fetch it
p = Popen('halcmd getp xbee.0.batt', shell=True, stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
log.debug("error code = %d" % p.returncode)
log.debug("stderr = %s" % err)
log.debug("stdout = %s" % out)

if out is None:
    #error
    pass
else:
    # log it
    log.info("logging to phant")
    url = 'http://phant.cursivedata.co.uk/input/L4y9DEbMzEUOdzPYlQ9NSJAXom4?private_key=87y0npg4jpt3xDgLz9YqT5xrPbq&batt=%s' % out
    r = requests.get(url)
    log.debug("get status = %d" % r.status_code)

log.info("finished")
