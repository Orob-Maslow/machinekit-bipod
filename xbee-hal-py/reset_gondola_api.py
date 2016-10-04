import time
import serial

"""
https://alselectro.wordpress.com/2014/07/01/xbee-s1-sending-remote-at-commands-using-api-packet-to-toggle-an-io/
http://serdmanczyk.github.io/XBeeAPI-PythonArduino-Tutorial/

control codes from the 'frame generator' of the xbee xctu program
have to be careful about ascii and hex values

protocol: 802.15.4
api mode: 1
frame type: 0x17 remote at commands

master xbee needs api mode set to 1:

ATAP1

slave doesn't need APIA like with the AT reset
"""

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=2.50
serial_port.baudrate=57600
serial_port.open()
print("port opened")

on = bytearray.fromhex('7E 00 10 17 01 00 13 A2 00 40 64 C3 C5 FF FE 02 64 30 05 6E')

off = bytearray.fromhex('7E 00 10 17 01 00 13 A2 00 40 64 C3 C5 FF FE 02 64 30 04 6F')

while True:
    serial_port.write(on)
    time.sleep(0.1)
    serial_port.write(off)
    time.sleep(0.1)
