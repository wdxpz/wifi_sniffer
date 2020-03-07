#!/usr/bin/env python

import time
import re
import requests
import threading
from Queue import Queue
from datetime import timedelta

import kismet_rest as KismetRest
from timeloop import Timeloop

import config

re_mac = '([0-9a-fA-F:?]{17})'

fields = [
    "kismet.device.base.manuf",
    "kismet.device.base.commonname",
    "kismet.device.base.macaddr",
    "kismet.device.base.type",
    "kismet.device.base.last_time",
    "kismet.device.base.signal"
]

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


upload_cache = Queue(maxsize=0)
write_cach_sigal = singal = threading.Event()

kr = KismetRest.KismetConnector(config.uri, username=config.user, password=config.password)

#wait for kismet service
while True:
    try:
        status = kr.system_status()
        print('found Kismet online!')
        break;
    except e:
        print('waiting Kismet online ....', end='\r')
        time.sleep(1)

tl = Timeloop()

#collect devices from kismet very config.collect_time_interval seconds 
@tl.job(interval=timedelta(seconds=config.collect_time_interval))
def collect_kismet():
    dlist = kr.smart_device_list(ts=time.time()-collect_time_interval)
    print('\n\nstart to collect devices...!')
    print('found original device records: {}'.format(len(dlist)))

    temp_cache = []
    for d in dlist:
        temp_cache.append({
            'mac': d['kismet.device.base.macaddr'],
            'name': d["kismet.device.base.commonname"],
            'manuf': d['kismet.device.base.manuf'],
            'type': d['kismet.device.base.type'],
            'signal': d['kismet.device.base.signal']['kismet.common.signal.last_signal'],
            'time': d['kismet.device.base.last_time']
            }
        )
        #print('found new device {}'.format(drecords[d['kismet.device.base.macaddr']]))
    print('generate  device records: {}'.format(len(drecords)))
    upload_cache.put(temp_cache)

#upload to data center
@tl.job(interval=timedelta(seconds=config.upload__time_interval))
def upload():
    records = []
    while not upload_cache.empty():
        records += upload_cache.get()
        upload_cache.task_done()

    print('consume device records: {}'.format(len(records)))
    t = threading.Thread(target=upload, args=(records,))
    t.start()

def upload(devices):
    # data to be sent to api
    #data = {'data':devices}
    data = devices
    # sending post request and saving response as response object
    try:
        #r = requests.post(url = config.upload_endpoint, data = data)
        print('upload {} devices'.format(len(devices)))
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh, "\n on devices: \n", devices)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc, "\n on devices: \n", devices)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt, "\n on devices: \n", devices)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err, "\n on devices: \n", devices)


tl.start(block=True)

#kr.smart_device_list(ts=1, callback=per_device)
#kr.smart_device_list(fields=fields, callback=per_device)
 
