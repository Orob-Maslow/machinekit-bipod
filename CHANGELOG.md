# Tue Aug  2 22:18:15 CEST 2016

* Jon switches the gondola arms over
* Matt installs new software

Git tag is feat-button:

Software launched at boot with supervisior and button should work now.

* software stops and waits for press of button to start homing process
* next button press halts the machine 

## main changes

* supervisord bipod conf changed
* stop using adafruit library - couldn't get interrupts working reliably
* no longer setuid because of the above
* replaced with self-rolled simple system - hopefully not a bad idea
* moved setup.sh from root's crontab to machinekit and configure button interrupt
* start.sh boots the process after setting environment up
