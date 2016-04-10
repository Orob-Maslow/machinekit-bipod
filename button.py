#!/usr/bin/python
import Adafruit_BBIO.GPIO as GPIO
import logging
from control import send
import time
import socket

# create log file handler and set to debug
log = logging.getLogger('')
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
fh = logging.FileHandler('button.log')
fh.setFormatter(log_format)
log.addHandler(fh)

# button connected to this pin and +3.3v, with pulldown
# so if high, button is pressed
pin = "P9_12"
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# wait for bipod process to start
log.warning("waiting for bipod process to start")
while True:
    try:
        send('programs')
        break
    except socket.error:
        pass
    time.sleep(1)

def wait_for_button():
    log.warning("waiting for button press")
    while True:
        GPIO.wait_for_edge(pin, GPIO.RISING)
        # try to avoid noise issues that cause false triggers
        time.sleep(0.25)
        # if button still pressed
        if GPIO.input(pin):
            break

# first button we will send start
wait_for_button()
log.warning("button pressed, starting")
send('start')

# second button press will halt
wait_for_button()
log.warning("button pressed, halting")
send('halt')

GPIO.cleanup()
