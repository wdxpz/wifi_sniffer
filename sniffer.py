#!/usr/bin/env python

import time
import re
import requests
import threading
from queue import Queue
from datetime import timedelta, datetime

import kismet_rest as KismetRest

import config
from kafaka import sendMsg
from tsdb import DBHelper
from logger import getLogger
logger = getLogger('Wifi Sniffer')
logger.propagate = False

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
dbtool = DBHelper() if config.Enable_TSDB else None
last_collect_time = None

#TODO: need redis uri
r = redis.Redis()

def getLocation():
    if r is None:
        msg = "exit because Redis connection is failed!"
        logger.error(msg)
        raise Exception(msg)
    location = r.get(config.robot_id)

    return location

#collect devices from kismet very config.collect_time_mini_interval seconds 
def collect_kismet(interval):
    while True:

        time.sleep(interval)

        cur_time = time.time()
        if last_collect_time is None:
            last_collect_time = cur_time-interval

        try:
            dlist = kr.smart_device_list(ts=last_collect_time)
            #logger.info('found original device records: {}'.format(len(dlist)))
        except Exception as e:
            logger.error("read kismit db error! " + str(e))
            last_collect_time = cur_time
            continue

        last_collect_time = cur_time

        location = getLocation()
        if location is None or len(location)<2:
            continue

        temp_cache = []
        for d in dlist:
            temp_cache.append({
                'mac': d['kismet.device.base.macaddr'],
                'name': d["kismet.device.base.commonname"],
                'manuf': d['kismet.device.base.manuf'],
                'type': d['kismet.device.base.type'],
                'signal': d['kismet.device.base.signal']['kismet.common.signal.last_signal'],
                'time': datetime.fromtimestamp(d['kismet.device.base.last_time']).utcnow().isoformat("T"),
                'location': location
                }
            )
            logger.info('found new device {}'.format(temp_cache[len(temp_cache)-1]))
        logger.info('generate device records: {}'.format(len(temp_cache)))
        upload_cache.put(temp_cache)

#upload to data center
def upload2datacenter(interval):
    while True:
        time.sleep(interval)

        records = []
        while not upload_cache.empty():
            records += upload_cache.get()
            upload_cache.task_done()

        logger.info('consume device records: {}'.format(len(records)))
        if len(records) == 0:
            continue

        t = threading.Thread(target=sendMsg, args=(records,))
        t.start()

        if dbtool:
            t = threading.Thread(target=dbtool.upload, args=(records,))
            t.start()


def upload(devices):
    # data to be sent to api
    #data = {'data':devices}
    data = devices
    # sending post request and saving response as response object
    try:
        if dbtool:
            dbtool.upload(data)
            logger.info('upload influx {} devices'.format(len(devices)))
        
    except Exception as err:
        logger.info("Error: {}, during upload on devices: {}\n".format(err, devices))


if __name__ == 'main':
    #wait for kismet service
    while True:
        try:
            status = kr.system_status()
            logger.info('found Kismet online!')
            break;
        except e:
            logger.debug('waiting Kismet online ....\n')
            time.sleep(1)

    collect_t = threading.Thread(name='{}_collect_wifi_task'.format(config.robot_id), target=collect_kismet, args=(config.collect_time_mini_interval,))
    collect_t.setDaemon(True)
    collect_t.start()

    upload_t = threading.Thread(name='{}_upload_wifi_task'.format(config.robot_id), target=upload2datacenter, args=(config.upload_time_mini_interval,))
    upload_t.setDaemon(True)
    upload_t.start()