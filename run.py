import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS ServerConfig (Guild INTEGER unique, Prefix TEXT)")

async def get_prefix(bot, message):
	if message.guild:
		try:
			return server_config[message.guild.id]['prefix']
		except KeyError:
			return config['default_prefix']
	else:
		return config['default_prefix']

bot = commands.AutoShardedBot(command_prefix = commands.when_mentioned_or(get_prefix), case_insensitive = True, max_messages = 100)
bot.remove_command('help')

startup_extensions = ['cogs.BotLog', 'cogs.Events']
for cog in startup_extensions:
	try:
		bot.load_extension(cog)
	except Exception as e:
		print(e)

if len(config['botlog_webhook_url']) > 0 and config['botlog_webhook_url'].startswith('https://discordapp.com/api/webhooks/'):
	try:
		bot.load_extension('cogs.BotLog')
	except Exception as e:
		print(e)

if config['anti_bot_farm']['enabled'] == True:
	try:
		bot.load_extension('cogs.AntiFarm')
	except Exception as e:
		print(e)

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print('-------------')

@bot.event
async def on_message(message):
	if message.bot:
		return

	await bot.process_commands(message)


bot.run(config['token'])
