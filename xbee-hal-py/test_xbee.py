#!/usr/bin/python

import time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")
FMT = '<BHHHBBB'

# gondola flags
GOND_FLAG_CHARGE = 1
GOND_FLAG_SERVO_ENABLE = 2

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.05
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")

start_byte = 0xAA

def communicate(amount, flags):

    bind = struct.pack('<BBB', start_byte, amount, flags)
    logging.info("sending %d %d [%02x]", amount, flags, crc8_func(bind))
    bind = struct.pack('<BBBB', start_byte, amount, flags, crc8_func(bind))
    logging.debug(map(bin,bytearray(bind)))
    serial_port.write(bind)

    packet_size = struct.calcsize(FMT)
    response = serial_port.read(packet_size)
    if len(response) == packet_size:
        start, batt, rx_count, err_count, touch, flags, cksum = struct.unpack(FMT, response)
        bind = struct.pack('<BHHHBB', start, batt, rx_count, err_count, touch, flags)
        # check cksum
        if cksum == crc8_func(bind):
            logging.info( "start = %02x" % start)
            logging.info( "rx count = %d" % rx_count )
            logging.info( "err_count = %d" % err_count )
            logging.info( "flags = %d" % flags )
            logging.info( "batt = %d" % batt )
        else:
            logging.warning("bad cksum")
    else:
        logging.warning("wrong packet size got %d not %d" % (len(response), packet_size))

try:
    flags = GOND_FLAG_SERVO_ENABLE
    for val in range(20,160):
        communicate(val, flags)
        """
        communicate(113)
        communicate(114)
        communicate(115)
        communicate(113)
        communicate(114)
        communicate(115)
        """
    flags = 0 # GOND_FLAG_SERVO_ENABLE
    communicate(160, flags)

except KeyboardInterrupt:
    raise SystemExit
