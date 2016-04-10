"""
couldn't get Adafruit library working reliably
"""
import select
import time
import threading
import logging
import os

log = logging.getLogger(__name__)

# file to override button press
override = "/tmp/button"

class Interrupt(threading.Thread):

    def run(self):
        log.debug("button thread started")
        # hard coded p9.12
        f = '/sys/class/gpio/gpio60/value'
        # open & read the file
        fh = open(f)
        fh.read()
        poller = select.poll()
        poller.register(fh, select.POLLPRI | select.POLLERR)

        # wait until something changes and quit
        while True:
            events = poller.poll(1)
            if len(events):
                log.debug("button event")
                break

            # check override
            try:
                open(override)
                log.debug("button override")
                os.unlink(override)
                break
            except IOError:
                pass

        # finish
        fh.close()
        log.debug("button thread finished")

if __name__ == '__main__':
    thread = Interrupt()
    thread.start()
    print("blocking")
    thread.join()

    time.sleep(0.5)
    print("looping")
    thread = Interrupt()
    thread.daemon = True
    thread.start()
    while True:
        print("waiting")
        time.sleep(1)
        if not thread.isAlive():
            print("interrupted")
            thread.join()
            exit(1)
