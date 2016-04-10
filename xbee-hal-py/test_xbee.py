import time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.05
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")

packet_size = 8

def communicate(amount):
    bin = struct.pack('<B', amount)
    bin = struct.pack('<BB',amount, crc8_func(bin))
    serial_port.write(bin)

    response = serial_port.read(packet_size)
    if len(response) == packet_size:
        batt, rx_count, err_count, touch, cksum = struct.unpack('<HHHBB', response)
        bin = struct.pack('<HHHB', batt, rx_count, err_count, touch)
        # check cksum

try:
    for val in range(180):
        if val > 180: #max angle is 180
            val = 180
        if val < 0:
            val = 0
        logging.info(val)
        communicate(val)

except KeyboardInterrupt:
    raise SystemExit
