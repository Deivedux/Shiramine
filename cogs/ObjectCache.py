import time
import json
import sqlite3

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

start_time = time.time()
with open('configs/config.json') as json_data:
	config = json.load(json_data)

server_config_raw = c.execute("SELECT * FROM ServerConfig").fetchall()
server_config = {}
for i in server_config_raw:
	server_config[int(i[0])] = {'prefix': i[1]}
del server_config_raw
