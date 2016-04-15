import time
import serial

"""
couldn't get the switch over to work reliably, and saw enough issues while debugging to decide 
not to connect the output of the xbee to the atmega reset.

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
serial_port.timeout=1.50
serial_port.baudrate=57600
serial_port.open()
print("port opened")

def send_command(cmd):
    print("sending [%s]" % cmd.strip())
    serial_port.write(cmd)
    resp = serial_port.readline()
    resp = resp.strip()
    print("got [%s]" %  resp)
    if resp != 'OK':
        print("xbee not responding to %s" % cmd)
    return resp

"""
# enter AT mode
send_command('+++')
send_command('ATAP1\r')
# close session
send_command('ATCN\r') 
time.sleep(.5)
"""


on = bytearray.fromhex('7E 00 10 17 01 00 13 A2 00 40 64 C3 C5 FF FE 02 64 30 05 6E')

off = bytearray.fromhex('7E 00 10 17 01 00 13 A2 00 40 64 C3 C5 FF FE 02 64 30 04 6F')

print("off")
serial_port.write(off)
time.sleep(.5)
print("on")
serial_port.write(on)

"""
serial_port.flushOutput()
serial_port.flushInput()

time.sleep(.5)

#num_byte = serial_port.inWaiting()
#serial_port.read(num_byte)
send_command('+++')
send_command('ATAP0\r')
send_command('ATCN\r') 
"""
