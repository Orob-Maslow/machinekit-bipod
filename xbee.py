#!/usr/bin/python
import hal, time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")


def send_packet(amount):
    bin = struct.pack('<B', amount)
    bin = struct.pack('<BB',amount, crc8_func(bin))
    serial_port.write(bin)

h = hal.component("xbee")
h.newpin("in", hal.HAL_FLOAT, hal.HAL_IN)
h.newparam("scale", hal.HAL_FLOAT, hal.HAL_RW)

logging.info("scale = %d" % h['scale'])


serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=2
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")

h.ready()
logging.info("hal ready")

try:
    while 1:
        time.sleep(0.05)
	val = h['in'] * h['scale']
        if val >= 0 and val <= 255:
	    send_packet(val)
except KeyboardInterrupt:
    raise SystemExit
