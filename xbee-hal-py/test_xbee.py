import time
import logging
import serial
import struct
import crcmod

logging.basicConfig(level=logging.DEBUG)
logging.info("xbee started")

crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")
FMT = '<HHHBBB'

# gondola flags
GOND_FLAG_CHARGE = 1
GOND_FLAG_SERVO_ENABLE = 2

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=0.01
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")


def communicate(amount, flags):

    bin = struct.pack('<BB', amount, flags)
    logging.info("sending %d %d [%02x]", amount, flags, crc8_func(bin))
    bin = struct.pack('<BBB',amount, flags, crc8_func(bin))
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

except KeyboardInterrupt:
    raise SystemExit
