import serial
import struct
import crcmod
import logging
import time

logging.basicConfig(level=logging.DEBUG)
crc8_func = crcmod.predefined.mkPredefinedCrcFun("crc-8-maxim")

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=2
serial_port.baudrate=57600
serial_port.open()
logging.info("port opened")


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

def test_move():
    for i in range(10): 
        logging.info(i)
        time.sleep(0.1)
        send_packet(i * 10)
        b = get_packet()
        logging.info("batt = %d" % b)

if __name__ == '__main__':
    test_move()
