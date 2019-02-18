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
for i in server_config_raw:
	server_config[int(i[0])] = {'prefix': i[1], 'language': i[2]}
del server_config_raw

response_string = {}
for i in os.listdir('./languages'):
	if i.endswith('.json'):
		with open(os.path.join('./languages', i)) as file:
			response = json.load(file)
		response_string[i.strip('.json')] = response

def get_lang(ctx):
	try:
		return response_string[server_config[ctx.guild.id]['language']]
	except:
		return response_string['english']
