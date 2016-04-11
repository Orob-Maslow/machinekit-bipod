import pickle
import sys
import os
# make this into lib
tmp_file = '/tmp/pos.pkl'
pos_file = '/home/machinekit/pos.pkl'
def atomic_write(pos):
	with open(tmp_file, 'w') as fh:
		pickle.dump(pos, fh)
		# make sure that all data is on disk
		fh.flush()
		os.fsync(fh.fileno()) 

	os.rename(tmp_file, pos_file)

pos = { 'l' : int(sys.argv[1]), 'r' : int(sys.argv[2])}
print(pos)
atomic_write(pos)

