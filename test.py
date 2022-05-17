#!/usr/bin/env python

import time
import kismet_rest as KismetRest
import argparse


def per_device(d):
    for k in d.keys():
        print('name: {}; mac: {}; manuf: {}; type: {}; max_signal: {}; timestamp: {}; {:.2f} ago'.format(
            d["kismet.device.base.commonname"],
            d['kismet.device.base.macaddr'],
            d['kismet.device.base.manuf'],
            d['kismet.device.base.type'],
            d['kismet.device.base.signal']['kismet.common.signal.max_signal'],
            d['kismet.device.base.last_time'],
            time.time() - d['kismet.device.base.last_time']))

uri = "http://localhost:2501"

parser = argparse.ArgumentParser(description='Kismet demo code')

parser.add_argument('--uri', action="store", dest="uri")

results = parser.parse_args()

if results.uri is not None:
    uri = results.uri

kr = KismetRest.KismetConnector(uri, username="kismet", password="kismet")

fields = [
    "kismet.device.base.manuf",
    "kismet.device.base.commonname",
    "kismet.device.base.macaddr",
    "kismet.device.base.type",
    "kismet.device.base.last_time",
    "kismet.device.base.signal"
]

kr.smart_device_list(ts=1, callback=per_device)
#kr.smart_device_list(fields=fields, callback=per_device)
