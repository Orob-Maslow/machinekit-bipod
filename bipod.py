#!/usr/bin/env python
from subprocess import Popen, PIPE
from interrupt import Interrupt
import os
import glob
import logging
import linuxcnc
import time
import pickle
import SocketServer
from Queue import Queue
from threading import Thread

HOST = 'localhost'
PORT = 10001

# msq queues
q_recv = Queue(maxsize=0)
q_send = Queue(maxsize=0)

# setup linuxcnc control/feedback channels
# http://linuxcnc.org/docs/2.6/html/common/python-interface.html for more details
com = linuxcnc.command()
sta = linuxcnc.stat()
err = linuxcnc.error_channel()

class ShutdownException(Exception):
    pass
class QuitException(Exception):
    pass

# where the ngc files are
dir = '/tmp/gcodes/*ngc'

# gondola flags
GOND_FLAG_CHARGE = 1
GOND_FLAG_SERVO_ENABLE = 2

# count how many programs have been run
program_count = 0
log_interval = 10 #seconds

# setup logging
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

# this should come from .hal
width = 2140 
g54 = { 'x': 0, 'y': 0, 'z': 0 } # this is where the g54 0,0 point will be
# what files to run to charge the gondola battery
dir_path = os.path.dirname(os.path.realpath(__file__))
charge_gcode = dir_path + '/charge.ngc'
precharge_gcode = dir_path + '/precharge.ngc'

#################################################
# start of functions

def wait_till_done():
    while True:
        sta.poll()
        time.sleep(1)
        if sta.interp_state == linuxcnc.INTERP_IDLE:
            log.info("finished")
            break

def run_program(file):
    log.info("starting program %d: %s" % (program_count, file))
    log.debug("changing to auto mode")
    com.mode(linuxcnc.MODE_AUTO)
    com.wait_complete() # wait until mode switch executed
    sta.poll()

    if sta.task_mode == linuxcnc.MODE_AUTO:
        log.debug("success")

    com.program_open(file)
    com.auto(linuxcnc.AUTO_RUN, 0) # second arg is start line
    wait_till_done()

def turn_on_servo():
    log.info("turning on servo")
    os.system("halcmd setp xbee.servo_enable 1")

def turn_off_servo():
    log.info("turning off servo")
    os.system("halcmd setp xbee.servo_enable 0")

def turn_on_charger():
    log.info("turning on charger")
    os.system("config-pin p9.13 hi")

def turn_off_charger():
    log.info("turning off charger")
    os.system("config-pin p9.13 lo")

def move_to_precharge():
    log.info("moving to precharge position")
    turn_off_charger()
    turn_on_servo()
    run_program(precharge_gcode)

def move_to_charge():
    log.info("moving to charging position")
    run_program(charge_gcode)

    # turn on power
    turn_on_charger()

    # turn off servo
    turn_off_servo()

    # wait for charge connection
    time.sleep(4)

    # then check if it's charging
    gond_flags = Popen('halcmd getp xbee.gond_flags', shell=True, stdout=PIPE).stdout.read().strip()
    gond_flags = int(gond_flags)
    if gond_flags & GOND_FLAG_CHARGE:
        log.info("docked and charging")
    else:
        log.warning("docked but not charging")

def set_g54():
    log.info("changing to mdi mode")
    com.mode(linuxcnc.MODE_MDI)
    com.wait_complete() # wait until mode switch executed
    sta.poll()
    if sta.task_mode == linuxcnc.MODE_MDI:
        log.debug("success")

    log.info("resetting g54 to x%d y%d z%d" % (g54['x'], g54['y'], g54['z']))
    com.mdi("g10 l2 p1 x%d y%d" % (g54['x'], g54['y']))
    com.feedrate(200)

# run in a thread
def logger():
    last_log = time.time()
    while True:
        sta.poll()
        error = err.poll()
        if error:
            kind, text = error
            log.warning("error: %s" % text)
        """
        1 EXEC_ERROR
        2  EXEC_DONE
        3  EXEC_WAITING_FOR_MOTION
        4  EXEC_WAITING_FOR_MOTION_QUEUE
        5  EXEC_WAITING_FOR_PAUSE
        6  EXEC_WAITING_FOR_MOTION_AND_IO
        7  EXEC_WAITING_FOR_DELAY
        8  EXEC_WAITING_FOR_SYSTEM_CMD

        2, 3 (not much), 5 or 7 (lots)

        interp state
        1 to 4: INTERP_IDLE, INTERP_READING, INTERP_PAUSED, INTERP_WAITING
        mostly 1, 2 or 4

        state
        RCS_DONE, RCS_EXEC, RCS_ERROR.
        1, 2 (mostly) or 3 - worth investigating state 3

        inter errcode
        1 to 6: INTERP_OK, INTERP_EXIT, INTERP_EXECUTE_FINISH, INTERP_ENDFILE, INTERP_FILE_NOT_OPEN, INTERP_ERROR 
        always 0 so far
        """
        if time.time() - last_log > log_interval:
            last_log = time.time()
            log.debug("exec state %d, interp state %d, state %d, errcode %d, line in file %d" % (
                    sta.exec_state,
                    sta.interp_state,
                    sta.state,
                    sta.interpreter_errcode,
                    sta.motion_line))

        time.sleep(0.1)

# run in a thread
class CmdRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # put msg in receive queue
        cmd = self.request.recv(1024)
        log.debug("got cmd [%s]" % cmd)
        q_recv.put(cmd)

        # wait for a second for any reply we're going to send, main thread might be busy
        time.sleep(1)

        # if there is stuff to send back, send it
        while not q_send.empty():
            reply = q_send.get()
            log.debug("sending reply [%s]" % reply)
            self.request.send(reply)
        return

def check_cmd_message():
    if not q_recv.empty():
        msg = q_recv.get()
        msg = msg.strip()

        if msg == 'quit':
            log.warning("quitting")
            q_send.put("quit")
            raise QuitException()
        elif msg == 'halt':
            q_send.put("halt")
            raise ShutdownException()
        elif msg == 'programs':
            q_send.put(str(program_count))

        return msg

###########################################################################
# start of main

log.info("starting command server listening on [%s:%d]" % (HOST, PORT))
SocketServer.TCPServer.allow_reuse_address = True
server = SocketServer.TCPServer((HOST, PORT), CmdRequestHandler)

server_thread = Thread(target=server.serve_forever)
server_thread.setDaemon(True)
server_thread.start()

logger_thread = Thread(target=logger)
logger_thread.setDaemon(True)
logger_thread.start()

running = True

try:
    # wait for signal to start
    log.info("waiting for start command")
    while True:
        if check_cmd_message() == 'start':
            q_send.put("start")
            break
        time.sleep(0.1)

    # get state right
    com.state(linuxcnc.STATE_ESTOP_RESET)
    com.wait_complete() 
    com.state(linuxcnc.STATE_ON)
    com.wait_complete()

    # home all
    log.info("homing all..")
    com.home(0)
    com.home(1)
    com.home(2)

    while not sta.homed[0:3] == (1,1,1):
        sta.poll()
        time.sleep(0.1)
        msg = check_cmd_message() 

    # switch to world mode
    log.info("teleop mode")
    com.teleop_enable(1)
    com.wait_complete()
    set_g54()

    # to do homing, uncomment these lines
    # while True:
    #     log.info("waiting")
    #    time.sleep(1)

    # move to charge pos
    move_to_precharge()

    move_to_charge()

    # wait for files to appear
    while running:
        # here we can request program count, quit or shutdown
        msg = check_cmd_message()

        files = glob.glob(dir)
        if len(files) == 0:
            if int(time.time()) % 10 == 0:
                log.info("no files, sleeping")
            time.sleep(1)
            continue

        set_g54() # in case the program changed it
        move_to_precharge()
        run_program(files[0])
        while True:
            sta.poll()
            if sta.interp_state == linuxcnc.INTERP_IDLE:
                log.info("finished")
                break
            time.sleep(0.1)
            # here we can skip the program
            msg = check_cmd_message()
            if msg == 'skip':
                q_send.put("skip")
                break

        program_count += 1

        os.remove(files[0])
        move_to_precharge()
        move_to_charge()

except KeyboardInterrupt:
    log.info("keyboard interrupt!")
except QuitException:
    log.warning("quitting")
except ShutdownException:
    log.warning("shutdown")
    # do the shutdown
    os.system("sudo halt")
except Exception as e:
    log.error("unexpected exception! %s" % e)

turn_off_charger()
log.info("done")
