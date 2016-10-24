"""
how to toggle a remote pin on an xbee
http://angryelectron.com/force-local-xbee-transmit-io-sample/ 

after setting up and checking transparent works,

remote needs

ATIAFFFF or ATIA[address of master] # allow master to control io
ATD05   # turn gpio0 into digital out high (low works too)

"""
import time
import serial

serial_port=serial.Serial()
serial_port.port='/dev/ttyO1'
serial_port.timeout=2.50
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

# enter AT mode
send_command('+++')

# turn on periodic sampling (500ms)
send_command('ATIR01F4\r')

# turn local pin low
send_command('ATD04\r') 

# exit AT mode
send_command('ATCN\r')

# wait for a moment longer than necessary
time.sleep(0.6)

# enter AT mode
send_command('+++')

# turn local pin high
send_command('ATD05\r') 

# exit AT mode
send_command('ATCN\r')

# wait for a moment longer than necessary
time.sleep(0.6)

# enter AT mode
send_command('+++')

# turn off periodic sampling
send_command('ATIR0\r')
