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

def get_packet():
    response = serial_port.read(3)
    if response:
        batt, cksum = struct.unpack('<HB', response)
        bin = struct.pack('<H', batt)
        # check cksum
        assert cksum == crc8_func(bin)
        return batt


h = hal.component("xbee")
h.newpin("in", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("batt", hal.HAL_FLOAT, hal.HAL_OUT)
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
        val += 10 #TODO 
        if val > 255:
            val = 255
        if val < 0:
            val = 0
        send_packet(val)
        batt = get_packet()
        if batt is not None:
            h['batt'] = batt
        else:
            h['batt'] = -1


except KeyboardInterrupt:
    raise SystemExit
