robot_id = 'tb3_0'
id = robot_id+'-wifi01'

uri = "http://localhost:2501"
user = 'kismet'
password = 'kismet'
collect_time_interval = 1
upload_time_interval = 1
collect_time_mini_interval = 0.2
upload_time_mini_interval = 0.5

#tsdb
Enable_TSDB = True
upload_URL = 'www.bestfly.ml'
upload_PORT = 8086
upload_DB = 'robot'
upload_table = 'wifi_sniffer'

#kafaka
topic = "wifi-sniffer-test"
brokers = ["192.168.12.146:9092"] # current internal brokers(actually 3 brokers behind)
block_waiting_time = 1

#redis
redis_host = "192.168.12.146"
redis_port = "6379"

#log file
log_file = '/home/pi/projects/wifi_sniffer/wifi_sniffer.log'
