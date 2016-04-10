"""
couldn't get Adafruit library working reliably
"""
import select
import threading

class Interrupt(threading.Thread):

    def run(self):
        # hard coded p9.12
        f = '/sys/class/gpio/gpio60/value'
        # open & read the file
        fh = open(f)
        fh.read()
        poller = select.poll()
        poller.register(fh, select.POLLPRI | select.POLLERR)
        events = poller.poll()
        # wait until something changes and quit
        fh.close()

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
