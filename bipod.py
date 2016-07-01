#!/usr/bin/env python
from subprocess import Popen, PIPE
import utils
import os
import glob
import logging
import linuxcnc
import time
import pickle


log = logging.getLogger('')
log.setLevel(logging.DEBUG)

# create console handler and set level to info
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# create file handler and set to debug
fh = logging.FileHandler('bipod.log')
fh.setFormatter(log_format)
log.addHandler(fh)

log.info("started")

# this should come from .hal
width = 2265 
g54 = { 'x': width/2, 'y': 1390 } # this is where the g54 0,0 point will be
charge_pos = { 'x' : 0, 'y' : 0 } # relative to g54

# lengthen strings if necessary
"""
def pre_home_jog():
    log.info("pre home jog")
    jog = 100 #mm
    velocity = 100
    com = linuxcnc.command()
    sta = linuxcnc.stat()
    home_x, home_y = 'TRUE', 'TRUE'
    while home_x == 'TRUE' and home_y == 'TRUE':
        # jog down a bit anyway in case on top of home switches
        if home_x == 'TRUE':
            com.jog(linuxcnc.JOG_INCREMENT, 0, velocity, jog)
        if home_y == 'TRUE':
            com.jog(linuxcnc.JOG_INCREMENT, 1, velocity, jog)
        com.wait_complete() 
        home_x = Popen('halcmd gets home-x', shell=True, stdout=PIPE).stdout.read().strip()
        home_y = Popen('halcmd gets home-y', shell=True, stdout=PIPE).stdout.read().strip()
        log.info("x: %s y: %s" % (home_x, home_y))
"""

def run_program(file):
    log.debug("changing to auto mode")
    com.mode(linuxcnc.MODE_AUTO)
    com.wait_complete() # wait until mode switch executed
    sta.poll()

    if sta.task_mode == linuxcnc.MODE_AUTO:
        log.debug("success")

    com.program_open(file)
    com.auto(linuxcnc.AUTO_RUN, 0) # second arg is start line
    while True:
        sta.poll()
        log.debug("exec state %d" % sta.exec_state)
        log.debug("interp state %d" % sta.interp_state)
        log.debug("state %d" % sta.state)
        log.debug("interp errcode %d" % sta.interpreter_errcode)
        time.sleep(10)
        if sta.interp_state == linuxcnc.INTERP_IDLE:
            log.info("finished")
            break


def move_to_charge():
    log.info("moving back to charging position")
    com.mode(linuxcnc.MODE_MDI)
    com.wait_complete() # wait until mode switch executed
    sta.poll()
    if sta.task_mode == linuxcnc.MODE_MDI:
        log.debug("success")

    log.info("sending gcode x%d y%d" % (charge_pos['x'], charge_pos['y']))
    com.mdi("g0 x%d y%d" % (charge_pos['x'], charge_pos['y']))

    while True:
        sta.poll()
        log.debug("exec state %d" % sta.exec_state)
        log.debug("interp state %d" % sta.interp_state)
        log.debug("state %d" % sta.state)
        log.debug("interp errcode %d" % sta.interpreter_errcode)
        time.sleep(5)
        if sta.interp_state == linuxcnc.INTERP_IDLE:
            break

# Usage examples for some of the commands listed below:
com = linuxcnc.command()
sta = linuxcnc.stat()

com.state(linuxcnc.STATE_ESTOP_RESET)
com.wait_complete() 
com.state(linuxcnc.STATE_ON)
com.wait_complete()

log.info("homing all")
com.home(0)
com.home(1)
com.home(2)

while not sta.homed[0:3] == (1,1,1):
    log.debug("homing...")
    sta.poll()
    time.sleep(1)

##############################

log.info("teleop mode")
com.teleop_enable(1)
com.wait_complete()
# doesn't seem to be a way to check if this worked

###############################

log.info("changing to mdi mode")
com.mode(linuxcnc.MODE_MDI)
com.wait_complete() # wait until mode switch executed
sta.poll()
if sta.task_mode == linuxcnc.MODE_MDI:
    log.debug("success")

log.info("resetting g54 to x%d y%d" % (g54['x'], g54['y']))
com.mdi("g10 l2 p1 x%d y%d" % (g54['x'], g54['y']))
com.feedrate(200)
move_to_charge()

###############################


dir = '/tmp/gcodes/*ngc'
while True:
    files = glob.glob(dir)
    if len(files) == 0:
        log.info("no files, sleeping")
        time.sleep(10)
        continue

    log.info("starting program: %s" % files[0])
    run_program(files[0])

    os.remove(files[0])
    move_to_charge()

log.info("done")
