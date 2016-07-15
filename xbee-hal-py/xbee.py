#!/usr/bin/python
import hal, time
import logging
import serial
import struct
import crcmod

FMT = '<HHHBBB'

# max servo angle
MAX_VAL = 170

# setup log
log = logging.getLogger('')
log.setLevel(logging.DEBUG)

# create console handler and set level to info
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# create file handler and set to debug
fh = logging.FileHandler('xbee.log')
fh.setFormatter(log_format)
log.addHandler(fh)

log.info("xbee HAL component started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")

h = hal.component("xbee")
# these for control
h.newpin("pos", hal.HAL_FLOAT, hal.HAL_IN)
h['pos'] = 8 # default pen is up
h.newparam("scale", hal.HAL_FLOAT, hal.HAL_RW)
h['scale'] = 20 # default

# these for monitoring connection on bbb
h.newpin("rx-err", hal.HAL_U32, hal.HAL_OUT)
h.newpin("cksum-err", hal.HAL_U32, hal.HAL_OUT)

# these for monitoring connection on gondola
h.newpin("gond_batt", hal.HAL_FLOAT, hal.HAL_OUT)
h.newpin("gond_rx_count", hal.HAL_U32, hal.HAL_OUT)
h.newpin("gond_err_count", hal.HAL_U32, hal.HAL_OUT)
h.newpin("gond_flags", hal.HAL_U32, hal.HAL_OUT)
h.newpin("gond_touch", hal.HAL_U32, hal.HAL_OUT)

log.debug("scale = %d" % h['scale'])

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.10
serial_port.baudrate=57600
serial_port.open()
log.debug("port opened")

h.ready()
log.debug("hal ready")

def calc_batt(batt_adc):
    a_in = batt_adc * 3.3 / 1023
    R2 = 4700.0  # should be 100k but adjusted for RAIN impedance
    R1 = 10000.0
    batt_level = a_in / (R1 / (R1+R2))
    batt_level = round(batt_level, 2)
    return batt_level

def communicate(amount):
    bin = struct.pack('<B', amount)
    bin = struct.pack('<BB',amount, crc8_func(bin))
    serial_port.write(bin)

    packet_size = struct.calcsize(FMT)
    response = serial_port.read(packet_size)
    if len(response) == packet_size:
        batt, rx_count, err_count, touch, flags, cksum = struct.unpack(FMT, response)
        bin = struct.pack('<HHHBB', batt, rx_count, err_count, touch, flags)
        # check cksum
        if cksum == crc8_func(bin):
            h['gond_batt'] = calc_batt(batt)
            h['gond_rx_count'] = rx_count
            h['gond_err_count'] = err_count
            h['gond_touch'] = touch
            h['gond_flags'] = flags
        else:
            h['cksum-err'] += 1
    else:
        h['rx-err'] += 1

try:
    while 1:
        time.sleep(0.05)
        val = h['pos'] * h['scale']
        if val > MAX_VAL:
            val = MAX_VAL
        if val < 0:
            val = 0
        communicate(val)
except KeyboardInterrupt:
    raise SystemExit
    log.error("keyboard interrupt")
except Exception as e:
    log.error(e)

log.info("ending")
