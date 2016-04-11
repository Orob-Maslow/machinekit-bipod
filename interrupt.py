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
        fh.seek(0)
        poller = select.poll()
        poller.register(fh, select.POLLPRI | select.POLLERR)

        # wait until something changes and quit
        while True:
            events = poller.poll(1)
            if len(events):
                val = fh.read().strip()
                fh.seek(0)
                log.debug("%s = %s" % (f,val))
                if val == "1":
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
    log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(log_format)
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)

    thread = Interrupt()
    thread.start()
    log.info("blocking")
    thread.join()

    time.sleep(0.5)
    log.info("looping")
    thread = Interrupt()
    thread.daemon = True
    thread.start()
    while True:
        log.info("waiting")
        time.sleep(1)
        if not thread.isAlive():
            log.info("interrupted")
            thread.join()
            exit(1)
