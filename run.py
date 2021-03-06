import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('configs/Database.db', detect_types = sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

# CREATING ALL TABLES AND COLUMNS

c.execute("CREATE TABLE IF NOT EXISTS ServerConfig (Guild INTEGER unique, Prefix TEXT, Language TEXT, ImgFilter INTEGER, GreetMsg TEXT, GreetChannel INTEGER, GreetDel INTEGER, LeaveMsg TEXT, LeaveChannel INTEGER, LeaveDel INTEGER, GreetDmMsg TEXT, GreetDmToggle INTEGER, MemberPersistence INTEGER, ServerLogChannel INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS ModLogs (Guild INTEGER, CaseNumber INTEGER, Action TEXT, Offender INTEGER, Moderator INTEGER, CreatedAt TIMESTAMP)")
c.execute("CREATE TABLE IF NOT EXISTS URLFilters (Guild INTEGER, Channel INTEGER unique)")
c.execute("CREATE TABLE IF NOT EXISTS SelfAssignableRoles (Guild INTEGER, Role INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS MemberPersistence (Guild INTEGER, User INTEGER, Nickname TEXT, Roles TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS Currency (User INTEGER unique, Amount INTEGER, Claimed TIMESTAMP)")

try:
	c.execute("ALTER TABLE ServerConfig ADD ServerLogChannel INTEGER")
except sqlite3.OperationalError:
	pass

# END OF CREATING TABLES AND COLUMNS

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

bot = commands.AutoShardedBot(command_prefix = get_prefix, case_insensitive = True)
bot.remove_command('help')

startup_extensions = ['cogs.Events', 'cogs.Administration', 'cogs.Help', 'cogs.Utility', 'cogs.MemberPresence', 'cogs.OwnerOnly', 'cogs.Economy', 'cogs.ServerLog']
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
