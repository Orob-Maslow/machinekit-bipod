#!/bin/bash
export PATH=$PATH:/home/machinekit/bipod/xbee-hal-py/:/usr/local/bin/
export HOME=/home/machinekit/
export USER=machinekit
cd $HOME
date >> /tmp/start.log 2>&1
# start controller button
./bipod/button.py &
# replace process with bipod process
exec /usr/bin/linuxcnc /home/machinekit/bipod/bipod.ini >> /tmp/start.log 2>&1
