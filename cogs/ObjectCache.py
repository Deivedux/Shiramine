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
	server_config[int(db_response[0])]['member_persistence'] = int(db_response[12])

for i in server_config_raw:
	server_cache(i)
del server_config_raw

db_response = c.execute("SELECT * FROM URLFilters").fetchall()
url_filters = dict()

def url_filter_cache(db_response):
	try:
		url_filters[db_response[0]].append(db_response[1])
	except KeyError:
		url_filters[db_response[0]] = [db_response[1]]

for i in db_response:
	url_filter_cache(i)

response_string = {}
for i in os.listdir('./languages'):
	if i.endswith('.json'):
		with open(os.path.join('./languages', i)) as file:
			response = json.load(file)
		response_string[i.strip('.json')] = response

def get_lang(guild, response):
	try:
		return response_string[server_config[guild.id]['language']][response]
	except:
		return response_string['english'][response]
