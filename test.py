#!/usr/bin/env python
import os
import glob
import logging
logging.basicConfig(level=logging.DEBUG)
import linuxcnc
import time
logging.info("started")
import pickle

tmp_file = '/tmp/pos.pkl'
pos_file = '/home/machinekit/pos.pkl'
safe_home_pos = { 'l' : 350, 'r': 350 } # these should come from .ini
width = 520 # should come from .hal
g54 = { 'x': width/2, 'y': 240 } # this should be calculated from home string lengths
charge_pos = { 'x' : 0, 'y' : -120 } # relative to g54

def pre_home_jog():
	try:
		with open(pos_file) as fh:
			pos = pickle.load(fh)
	except IOError:
		logging.error("must have a valid position file")
		exit(1)

	logging.info("last known pos l=%f r=%f" % (pos['l'], pos['r']))
	logging.info("safe home pos  l=%f r=%f" % (safe_home_pos['l'], safe_home_pos['r']))
	l_jog = safe_home_pos['l'] - pos['l']
	r_jog = safe_home_pos['r'] - pos['r'] 
	logging.info("jogging l=%f r=%f" % (l_jog, r_jog))
	com = linuxcnc.command()
	sta = linuxcnc.stat()
	velocity = 20
	com.jog(linuxcnc.JOG_INCREMENT, 0, velocity, l_jog)
	com.jog(linuxcnc.JOG_INCREMENT, 1, velocity, r_jog)
	com.wait_complete() 

def atomic_write(pos):
	with open(tmp_file, 'w') as fh:
		pickle.dump(pos, fh)
		# make sure that all data is on disk
		fh.flush()
		os.fsync(fh.fileno()) 

	os.rename(tmp_file, pos_file)

def run_program(file):
	logging.info("changing to auto mode")
	com.mode(linuxcnc.MODE_AUTO)
	com.wait_complete() # wait until mode switch executed
	sta.poll()

	if sta.task_mode == linuxcnc.MODE_AUTO:
		logging.info("success")

	com.program_open(file)
	com.auto(linuxcnc.AUTO_RUN, 0) # second arg is start line
	while True:
		sta.poll()
		logging.info("exec state %d" % sta.exec_state)
		logging.info("interp state %d" % sta.interp_state)
		logging.info("state %d" % sta.state)
		logging.info("interp errcode %d" % sta.interpreter_errcode)
		# store the position on the disk in case of a power failure
		joints = sta.joint_actual_position
		pos = { 'l' : joints[0], 'r' : joints[1] }
		print(pos)
		atomic_write(pos)
		time.sleep(0.5)
		if sta.interp_state == linuxcnc.INTERP_IDLE:
			logging.info("finished")
			break

def move_to_charge():
	logging.info("moving back to charging position")
	com.mode(linuxcnc.MODE_MDI)
	com.wait_complete() # wait until mode switch executed
	sta.poll()
	if sta.task_mode == linuxcnc.MODE_MDI:
		logging.info("success")

	logging.info("sending gcode x%d y%d" % (charge_pos['x'], charge_pos['y']))
	com.mdi("g0 x%d y%d" % (charge_pos['x'], charge_pos['y']))

	while True:
		sta.poll()
		logging.info("exec state %d" % sta.exec_state)
		logging.info("interp state %d" % sta.interp_state)
		logging.info("state %d" % sta.state)
		logging.info("interp errcode %d" % sta.interpreter_errcode)
		time.sleep(1)
		if sta.interp_state == linuxcnc.INTERP_IDLE:
			break

# Usage examples for some of the commands listed below:
com = linuxcnc.command()
sta = linuxcnc.stat()

com.state(linuxcnc.STATE_ESTOP_RESET)
com.wait_complete() 
com.state(linuxcnc.STATE_ON)
com.wait_complete()

pre_home_jog()

sta.poll()
if not sta.axis[0]['homed']:
	logging.info("homing 0")
	com.home(0)
	com.wait_complete() 
	while not sta.axis[0]['homed']:
		logging.info("homing...")
		sta.poll()
		time.sleep(1)
if not sta.axis[1]['homed']:
	logging.info("homing 1")
	com.home(1)
	com.wait_complete() 
	while not sta.axis[1]['homed']:
		logging.info("homing...")
		sta.poll()
		time.sleep(1)
if not sta.axis[2]['homed']:
	logging.info("homing 2")
	com.home(2)
	com.wait_complete() 
	while not sta.axis[2]['homed']:
		logging.info("homing...")
		sta.poll()
		time.sleep(1)

##############################

logging.info("teleop mode")
com.teleop_enable(1)
com.wait_complete()
# doesn't seem to be a way to check if this worked

###############################

logging.info("changing to mdi mode")
com.mode(linuxcnc.MODE_MDI)
com.wait_complete() # wait until mode switch executed
sta.poll()
if sta.task_mode == linuxcnc.MODE_MDI:
	logging.info("success")

logging.info("resetting g54 to x%d y%d" % (g54['x'], g54['y']))
com.mdi("g10 l2 p1 x%d y%d" % (g54['x'], g54['y']))
move_to_charge()
com.feedrate(200)

###############################


dir = '/tmp/gcodes/*ngc'
while True:
	files = glob.glob(dir)
	if len(files) == 0:
		logging.info("no files, sleeping")
		time.sleep(10)
		continue

	logging.info("starting program: %s" % files[0])
	run_program(files[0])

	os.remove(files[0])
	move_to_charge()


logging.info("done")
