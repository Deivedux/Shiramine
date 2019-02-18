import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class Events:
	def __init__(self, bot):
		self.bot = bot

	async def on_ready(self):
		for guild in self.bot.guilds:
			try:
				c.execute()


def setup(bot):
	bot.add_cog(Events(bot))
