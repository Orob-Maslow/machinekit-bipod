#!/usr/bin/python
import hal, time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")

def communicate(amount):
    bin = struct.pack('<B', amount)
    bin = struct.pack('<BB',amount, crc8_func(bin))
    serial_port.write(bin)

    response = serial_port.read(3)
    if response:
        batt, cksum = struct.unpack('<HB', response)
        bin = struct.pack('<H', batt)
        # check cksum
        if cksum == crc8_func(bin):
            h['batt'] = batt
        else:
            h['cksum-err'] += 1
    else:
        h['rx-err'] += 1


h = hal.component("xbee")
h.newpin("pos", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("batt", hal.HAL_U32, hal.HAL_OUT)
h.newpin("cksum-err", hal.HAL_U32, hal.HAL_OUT)
h.newpin("rx-err", hal.HAL_U32, hal.HAL_OUT)
h.newparam("scale", hal.HAL_FLOAT, hal.HAL_RW)

logging.info("scale = %d" % h['scale'])

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.03
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")

h.ready()
logging.info("hal ready")

try:
    while 1:
        time.sleep(0.05)
        val = h['pos'] * h['scale']
        if val > 180: #max angle is 180
            val = 180
        if val < 0:
            val = 0
        communicate(val)

except KeyboardInterrupt:
    raise SystemExit
