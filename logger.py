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

# start with linuxcnc stuff
payload = { 'private_key': '87y0npg4jpt3xDgLz9YqT5xrPbq' }

log.info("started")

# define HAL stuff to log
pins = [
    { 'pin' : 'xbee.gond_batt', 'tag': 'pen_batt' },
    { 'pin' : 'xbee.gond_rx_count', 'tag': 'pen_rxcount' },
    { 'pin' : 'xbee.gond_err_count', 'tag': 'pen_errcount' },
    { 'pin' : 'xbee.cksum-err', 'tag': 'xbee_cksumerr' },
    { 'pin' : 'xbee.rx-err', 'tag': 'xbee_rxerr' },
    { 'pin' : 'xbee.gond_touch', 'tag': 'pen_touch' },

    ]

# fetch robot data from the HAL
for pin in pins:
    p = Popen('halcmd getp %s' % pin['pin'], shell=True, stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    log.debug("error code = %d" % p.returncode)
    log.debug("stderr = %s" % err)
    log.debug("stdout = %s" % stdout)

    payload[pin['tag']] = stdout

# get linuxcnc stats
import linuxcnc
try:
    sta = linuxcnc.stat()
    sta.poll()
    payload['cnc_execstate'] = sta.exec_state
    payload['cnc_interpstate'] = sta.interp_state
    payload['cnc_state'] = sta.state
    payload['xpos'] = sta.position[0]
    payload['ypos'] = sta.position[1]
    payload['zpos'] = sta.position[2]
except Exception as e:
    log.warning(e)
    payload['xpos'] = None
    payload['ypos'] = None
    payload['zpos'] = None

# log it
log.info("logging to phant")
url = 'http://phant.cursivedata.co.uk/input/L4y9DEbMzEUOdzPYlQ9NSJAXom4'
r = requests.get(url, params=payload)
log.debug("get status = %d" % r.status_code)

# do the linux stuff
payload = { "private_key": "45pby8Ab0RcjKmO9qAjYCwmnM8a" }

# get uptime
with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    payload["uptime"] = uptime_seconds
# load avg
with open('/proc/loadavg', 'r') as f:
    load_avg = float(f.readline().split()[0])
    payload["load_avg"] = load_avg
# temp
with open('/sys/class/hwmon/hwmon0/device/temp1_input', 'r') as f:
    cpu_temp = float(f.readline().split()[0])
    payload["cpu_temp"] = cpu_temp

# important processes
process_cmds = [ 
    { 'name': 'bipod_pid', 'cmd' : ['pgrep', '-f', 'bipod.py' ] },
    { 'name': 'linuxcnc_pid', 'cmd': ['pgrep', '-f', 'linuxcnc bipod.ini'] },
    { 'name': 'autossh_pid', 'cmd': ['pgrep', 'autossh'] }, ]

for process in process_cmds:
    p = Popen(process['cmd'], stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    try:
        pid = int(stdout)
        payload[process['name']] = True
    except ValueError:
        payload[process['name']] = False

# log it
url = 'http://phant.cursivedata.co.uk/input/3Nx3P463ZJhKwXqzNJKbCJqg13r'
r = requests.get(url, params=payload)
log.debug("get status = %d" % r.status_code)

log.info("finished")
