#!/usr/bin/python
"""
script to be run on a cronjob that fetches files from cursivedata
"""
import json
import sys
import time
import datetime
import argparse
import requests

ngc_dir = "/tmp/gcodes"

def fetch_data():
    url = args.url + '/endpoint_data/' + str(args.robot_id)
    if not args.no_consume:
        url += "/?consume=true"
    if args.verbose:
        print "fetching from", url
    gcodes = []
    count = 0
    while True:
        count += 1
        try:
            r = requests.get(url)
            if r.status_code == 200:
                gcode_file = "%s/%d.%d.ngc" % (args.ngc_dir, count, time.time())
                with open(gcode_file, 'w') as fh:
                    fh.write(r.text)
                if args.verbose:
                    print "[%d] writing to %s" % (count, gcode_file)
            elif r.status_code == 204:
                #end of the gcodes
                return
            elif r.status_code == 404:
                print("server has a problem with the gcodes")
                print("try refreshing URL by hand to clear bad gcode files")
            else:
                print "unexpected server response ", r.status_code 

        except requests.exceptions.ConnectionError, e:
            print >>sys.stderr, e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="fetch gcodes from cursivedata")
    parser.add_argument('--url',
        action='store', dest='url', default='http://cursivedata.co.uk',
        help="url of the server")
    parser.add_argument('--ngc-dir',
        action='store', dest='ngc_dir', default=ngc_dir,
        help="directory for gcodes")
    parser.add_argument('--no-consume',
        action='store_const', const=True, dest='no_consume', default=False,
        help="don't consume all the gcodes ")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=True,
        help="verbose")
    parser.add_argument('--send-status',
        action='store_const', const=True, dest='sendstatus', default=False,
        help="send current status of the robot to the server")
    parser.add_argument('--robot-id',
        action='store', dest='robot_id', type=int, default=None, required=True,
        help="override robot id")

    args = parser.parse_args()

    print "started ", datetime.datetime.now()
    gcodes = []

    if args.sendstatus:
        response = update_robot_status()

    gcodes = fetch_data()
