# bipod machinekit config

inspired by:

* http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Koppi%27s_Toy
* http://linuxcnc.org/docs/html/motion/kinematics.html
* https://github.com/Chojins/LinuxCNC-Polargraph

# machinekit

This config has been changed for machinekit on the beaglebone black. This makes
use of the PRU realtime step generation for fast stepping.

# pen holder / gondola

The gondola uses an Xbee radio to raise and lower the pen. A python userspace
HAL component was tried first but had too much lag. The component was ported to
C and run in it's own thread every 50ms.

# drawings / controller

Rather than use axis, a [Python program](bipod.py) is used to draw gcode files,
log information, handle homing and gondola charging.

# todo

sta.state 1, 2 or 3
http://linuxcnc.org/docs/2.6/html/common/python-interface.html

3 is rcs error, which happens with estop

then system keeps running even after estop unpressed, because not enabled
