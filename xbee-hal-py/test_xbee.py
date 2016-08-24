import time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")
FMT = '<HHHBBB'

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.01
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")


def communicate(amount):
    bin = struct.pack('<B', amount)
    logging.info("sending %d [%02x/%02x]", amount, amount, crc8_func(bin))
    bin = struct.pack('<BB',amount, crc8_func(bin))
    serial_port.write(bin)

    packet_size = struct.calcsize(FMT)
    response = serial_port.read(packet_size)
    if len(response) == packet_size:
        batt, rx_count, err_count, touch, flags, cksum = struct.unpack(FMT, response)
        bin = struct.pack('<HHHBB', batt, rx_count, err_count, touch, flags)
        # check cksum
        if cksum == crc8_func(bin):
            logging.info( "rx count = %d" % rx_count )
            logging.info( "err_count = %d" % err_count )
            logging.info( "flags = %d" % flags )
            logging.info( "touch = %d" % touch )
        else:
            logging.warning("bad cksum")
    else:
        logging.warning("wrong packet size got %d not %d" % (len(response), packet_size))

try:
    for val in range(180):
        communicate(val)
        """
        communicate(113)
        communicate(114)
        communicate(115)
        communicate(113)
        communicate(114)
        communicate(115)
        """

except KeyboardInterrupt:
    raise SystemExit
