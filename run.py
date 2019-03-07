import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('configs/Database.db', detect_types = sqlite3.PARSE_DECLTYPES)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS ServerConfig (Guild INTEGER unique, Prefix TEXT, Language TEXT, ImgFilter INTEGER, GreetMsg TEXT, GreetChannel INTEGER, GreetDel INTEGER, LeaveMsg TEXT, LeaveChannel INTEGER, LeaveDel INTEGER, GreetDmMsg TEXT, GreetDmToggle INTEGER, MemberPersistence INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS SelfAssignableRoles (Guild INTEGER, Role INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS MemberPersistence (Guild INTEGER, User INTEGER, Nickname TEXT, Roles TEXT)")

from cogs.ObjectCache import config
from cogs.ObjectCache import server_config

async def get_prefix(bot, message):
	if message.guild:
		try:
			return commands.when_mentioned_or(server_config[message.guild.id]['prefix'])(bot, message)
		except KeyError:
			return commands.when_mentioned_or(config['default_prefix'])(bot, message)
	else:
		return commands.when_mentioned_or(config['default_prefix'])(bot, message)

bot = commands.AutoShardedBot(command_prefix = get_prefix, case_insensitive = True, max_messages = 100)
bot.remove_command('help')

startup_extensions = ['cogs.Events', 'cogs.Administration', 'cogs.Help', 'cogs.Utility', 'cogs.MemberPresence']
for cog in startup_extensions:
	try:
		bot.load_extension(cog)
	except Exception as e:
		print(e)

if len(config['botlog_webhook_url']) > 0:
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

	await bot.change_presence(activity = discord.Game(config['default_prefix'] + 'help'))

@bot.event
async def on_message(message):
	if message.author.bot:
		return

	await bot.process_commands(message)


bot.run(config['token'])
