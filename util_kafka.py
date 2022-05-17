import json
import copy
from kafka import KafkaProducer
import config

from logger import getLogger
logger = getLogger('Kafaka operation')
logger.propagate = False

producer = KafkaProducer(
    bootstrap_servers=config.brokers, compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

# just an example, you don't have to follow this format
payload = {
    'timestamp': None,
    "location": None,
    'id': config.id, 
    'mac': None,
    'name': None,
    'manuf': None,
    'type': None,
    'signal': None
}

def sendMsg(data):
    for record in data:
        body = copy.deepcopy(payload)
        body['timestamp'] = record['time']
        body['location'] = record['location']
        body['mac'] = record['mac']
        body['name'] = record['name']
        body['manuf'] = record['manuf']
        body['type'] = record['type']
        body['signal'] = record['signal']

        try:
            future = producer.send(config.topic, key="".encode(), value=body)
            # Block until a single message is sent (or timeout)
            result = future.get(timeout=config.block_waiting_time)
            logger.info('Kafaka operation : send wifi records record {}! '.format(body))
        except Exception as e:
            logger.error('Kafaka operation : send wifi records record error! ' + str(e))