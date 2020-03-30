#!/usr/bin/env python

import time
import re
import requests
import threading
from queue import Queue
from datetime import timedelta, datetime

import kismet_rest as KismetRest
from timeloop import Timeloop

import config
from tsdb import DBHelper

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
dbtool = DBHelper()

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
    dlist = kr.smart_device_list(ts=time.time()-config.collect_time_interval)
    #print('found original device records: {}'.format(len(dlist)))

    temp_cache = []
    for d in dlist:
        temp_cache.append({
            'mac': d['kismet.device.base.macaddr'],
            'name': d["kismet.device.base.commonname"],
            'manuf': d['kismet.device.base.manuf'],
            'type': d['kismet.device.base.type'],
            'signal': d['kismet.device.base.signal']['kismet.common.signal.last_signal'],
            'time': datetime.fromtimestamp(d['kismet.device.base.last_time']).utcnow().isoformat("T")
            }
        )
        print('found new device {}'.format(temp_cache[len(temp_cache)-1]))
    print('generate  device records: {}'.format(len(temp_cache)))
    upload_cache.put(temp_cache)

#upload to data center
@tl.job(interval=timedelta(seconds=config.upload_time_interval))
def upload2datacenter():
    records = []
    while not upload_cache.empty():
        records += upload_cache.get()
        upload_cache.task_done()

    print('consume device records: {}'.format(len(records)))
    if len(records) == 0:
        return
    t = threading.Thread(target=upload, args=(records,))
    t.start()

def upload(devices):
    # data to be sent to api
    #data = {'data':devices}
    data = devices
    # sending post request and saving response as response object
    try:
        dbtool.upload(data)
        print('upload {} devices'.format(len(devices)))
    except Exception as err:
        print ("Error: ",err, "\n on devices: \n", devices)

tl.start(block=True)

#kr.smart_device_list(ts=1, callback=per_device)
#kr.smart_device_list(fields=fields, callback=per_device)
 
