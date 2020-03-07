#!/usr/bin/env python

import time
import kismet_rest as KismetRest
import argparse


def per_device(d):
    # print d
    # for k in d.keys():
    #     print k

    if d["kismet.device.base.type"] != "Wi-Fi AP":
        print("%s %.2fs ago" % (d['kismet.device.base.macaddr'], (
            time.time() - d['kismet.device.base.last_time'])))


uri = "http://localhost:2501"

parser = argparse.ArgumentParser(description='Kismet demo code')

parser.add_argument('--uri', action="store", dest="uri")

results = parser.parse_args()

if results.uri is not None:
    uri = results.uri

kr = KismetRest.KismetConnector(uri, username="kismet", password="kismet")

fields = [
    "kismet.device.base.type", "kismet.device.base.macaddr",
    "kismet.device.base.last_time"
]

# kr.smart_device_list(ts=-60, callback=per_device)
kr.smart_device_list(fields=fields, callback=per_device)
