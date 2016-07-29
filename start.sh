#!/bin/bash
export PATH=$PATH:/home/machinekit/bipod/xbee-hal-py/
export HOME=/home/machinekit/
export USER=machinekit
exec /usr/bin/linuxcnc /home/machinekit/bipod/bipod.ini >> /tmp/startlog 2>&1
