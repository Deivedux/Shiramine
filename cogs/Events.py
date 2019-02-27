import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import server_cache

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

sql_insert = "INSERT INTO ServerConfig (Guild, Language, AntiInvite, AntiURL, GreetMsg, GreetDel, GreetToggle, LeaveMsg, LeaveDel, LeaveToggle, GreetDmMsg, GreetDmToggle) VALUES ({0}, 'english', 0, 0, 'Welcome &user& to **&server&**!', 0, 0, '&user& has left.', 0, 0, 'Welcome to **&server&**!', 0)"

class Events:
	def __init__(self, bot):
		self.bot = bot

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

		for i in server_config.keys():
			guild = self.bot.get_guild(i)
			if not guild:
				del server_config[i]

	async def on_guild_join(self, guild):
		conf = c.execute("SELECT * FROM ServerConfig WHERE Guild = " + str(guild.id)).fetchone()
		if not conf:
			c.execute(sql_insert.format(str(guild.id)))
			conn.commit()

			conf = c.execute("SELECT * FROM ServerConfig WHERE Guild = " + str(guild.id)).fetchone()
			server_cache(conf)
		else:
			server_cache(conf)

	async def on_guild_remove(self, guild):
		del server_config[guild.id]


def setup(bot):
	bot.add_cog(Events(bot))
