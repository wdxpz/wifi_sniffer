#!/usr/bin/env python

import time
import re
import requests
import threading
from queue import Queue
from datetime import timedelta, datetime

import redis
import kismet_rest as KismetRest

import config
from util_kafka import sendMsg
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

redis_connector = redis.Redis(host=config.redis_host, port=config.redis_port, db=0)

def per_device(d):
    for _ in d.keys():
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

def getLocation():
    res = redis_connector.hgetall(config.robot_id)
    logger.info('redis return {}'.format(res))
    if res is None or 'location'.encode() not in res.keys():
        return None

    logger.info('location: {}'.format(res['location'.encode()].decode()))
    return res['location'.encode()].decode()

#collect devices from kismet very config.collect_time_mini_interval seconds 
def collect_kismet(interval):
    global last_collect_time

    while True:
        time.sleep(interval)

        cur_time = time.time()
        if last_collect_time is None:
            last_collect_time = cur_time-interval

        try:
            dlist = kr.smart_device_list(ts=last_collect_time)
            # logger.info('found original device records: {}'.format(len(dlist)))
        except Exception as e:
            logger.error("read kismit db error! " + str(e))
            last_collect_time = cur_time
            continue
        if len(dlist)==0:
            continue

        last_collect_time = cur_time

        location = getLocation()
        if location is None or len(location)<2:
            continue

        temp_cache = []
        for d in dlist:
            if 'kismet.device.base.signal' not in d.keys():
                logger.info("device without signal value, ingnore!")
                continue
            temp_cache.append({
                'mac': d['kismet.device.base.macaddr'],
                'name': d["kismet.device.base.commonname"],
                'manuf': d['kismet.device.base.manuf'],
                'type': d['kismet.device.base.type'],
                'signal': d['kismet.device.base.signal']['kismet.common.signal.last_signal'],
                'time': d['kismet.device.base.last_time'], #datetime.fromtimestamp(d['kismet.device.base.last_time']).utcnow().isoformat("T"),
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

        
        if len(records) == 0:
            continue

        logger.info('consume device records: {}'.format(len(records)))

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


if __name__ == '__main__':
    #wait for kismet service
    while True:
        try:
            status = kr.system_status()
            logger.info('found Kismet online!')
            break
        except Exception as e:
            logger.debug('waiting Kismet online ....\n')
            time.sleep(1)

    collect_t = threading.Thread(name='{}_collect_wifi_task'.format(config.robot_id), target=collect_kismet, args=(config.collect_time_mini_interval,))
    # collect_t.setDaemon(True)
    collect_t.start()

    upload_t = threading.Thread(name='{}_upload_wifi_task'.format(config.robot_id), target=upload2datacenter, args=(config.upload_time_mini_interval,))
    # upload_t.setDaemon(True)
    upload_t.start()
