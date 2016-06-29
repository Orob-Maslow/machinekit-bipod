#!/usr/bin/python

from subprocess import Popen, PIPE
import requests

# fetch it
batt = Popen('halcmd getp xbee.0.batt', shell=True, stdout=PIPE).stdout.read()

if batt is None:
    #error
    pass
else:
    # log it
    url = 'http://phant.cursivedata.co.uk/input/L4y9DEbMzEUOdzPYlQ9NSJAXom4?private_key=87y0npg4jpt3xDgLz9YqT5xrPbq&batt=%s' % batt
    r = requests.get(url)
