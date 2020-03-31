import copy
import datetime
from influxdb import InfluxDBClient

import config

body_wifi = {
    'measurement': config.upload_table,
    'time': 0,
    'tags': {
        'mac': 0
    },
    'fields':{
        'name': 0,
        'manuf': 0,
        'type': 0,
        'signal': 0
    }
}

class DBHelper():
    def __init__(self, db_url=config.upload_URL, port=config.upload_PORT, dbname=config.upload_DB):
        self.client = InfluxDBClient(host=db_url, port=port, database=dbname)

    def writeWifiRecords(self, wifi_records):
        records = []
        if len(wifi_records) == 0:
            return

        for record in wifi_records:
            body = copy.deepcopy(body_wifi)
            
            mac, name, manuf, type, signal, time = record['mac'], record['name'], record['manuf'], \
                                                          record['type'], record['signal'], record['time']

            body['time'] = time
            body['tags']['mac'] = mac
            body['fields']['name'] = name
            body['fields']['manuf'] = manuf
            body['fields']['type'] = type
            body['fields']['signal'] = signal

            records.append(body)

        try:
            self.client.write_points(records)
        except Exception as e:
            print('DB operation: write robot position record error!', e)
    
    def emptyWifiRecords(self):
        self.client.query("delete from {};".format(config.upload_table))
        # self.client.query("drop measurement {}".format(config.upload_table))

    def getAllWifiRecords(self):
        resutls = self.client.query('select * from {};'.format(config.upload_table))
        return resutls

    def upload(self, wifi_records):
        self.writeWifiRecords(wifi_records)
        print('DBHelper: sent {} wifi records'.format(len(wifi_records)))

if __name__ == '__main__':
    dbtool = DBHelper()

#    cur_time = datetime.datetime.utcnow().isoformat("T")

#    dbtool.emptyPos()
#    records = [(0,0,0,cur_time)]
#    dbtool.writePosRecord(0, 0, records)
    results = dbtool.getAllWifiRecords()
    print(results)
