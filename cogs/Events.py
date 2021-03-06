import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import server_cache
from cogs.ObjectCache import url_filters
from cogs.ObjectCache import url_filter_cache

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

sql_insert = "INSERT INTO ServerConfig (Guild, Language, GreetMsg, LeaveMsg, GreetDmMsg, GreetDmToggle, MemberPersistence) VALUES ({0}, 'english', 'Welcome &user& to **&server&**!', '&user& has left.', 'Welcome to **&server&**!', 0, 0)"

class Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		for guild in self.bot.guilds:
			try:
				c.execute(sql_insert.format(str(guild.id)))
			except sqlite3.IntegrityError:
				continue
			else:
				db_response = c.execute("SELECT * FROM ServerConfig WHERE Guild = " + str(guild.id)).fetchone()
				server_cache(db_response)

		conn.commit()

		configs = list()
		for i in server_config.keys():
			configs.append(i)
		for i in configs:
			guild = self.bot.get_guild(i)
			if not guild:
				del server_config[i]

		filters = list()
		for i in url_filters.keys():
			filters.append(i)
		for i in filters:
			guild = self.bot.get_guild(i)
			if not guild:
				del url_filters[i]

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		try:
			c.execute(sql_insert.format(str(guild.id)))
			conn.commit()
		except sqlite3.IntegrityError:
			pass

		conf = c.execute("SELECT * FROM ServerConfig WHERE Guild = " + str(guild.id)).fetchone()
		server_cache(conf)

		conf = c.execute("SELECT * FROM URLFilters WHERE Guild = " + str(guild.id)).fetchone()
		url_filter_cache(conf)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		del server_config[guild.id]


def setup(bot):
	bot.add_cog(Events(bot))
