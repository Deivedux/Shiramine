import time
import json
import sqlite3
import os

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

start_time = time.time()

with open('configs/config.json') as json_data:
	config = json.load(json_data)

server_config_raw = c.execute("SELECT * FROM ServerConfig").fetchall()
server_config = {}

def server_cache(db_response):
	server_config[int(db_response[0])] = {}
	if db_response[1]:
		server_config[int(db_response[0])]['prefix'] = db_response[1]
	server_config[int(db_response[0])]['language'] = db_response[2]
	if db_response[3]:
		server_config[int(db_response[0])]['img_filter'] = int(db_response[3])
	server_config[int(db_response[0])]['anti_invite'] = int(db_response[4])
	server_config[int(db_response[0])]['anti_url'] = int(db_response[5])

for i in server_config_raw:
	server_cache(i)

del server_config_raw

response_string = {}
for i in os.listdir('./languages'):
	if i.endswith('.json'):
		with open(os.path.join('./languages', i)) as file:
			response = json.load(file)
		response_string[i.strip('.json')] = response

def get_lang(msg, response):
	try:
		return response_string[server_config[msg.guild.id]['language']][response]
	except:
		return response_string['english'][response]
