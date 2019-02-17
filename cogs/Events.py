import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class Events:
	def __init__(self, bot):
		self.bot = bot


def setup(bot):
	bot.add_cog(Events(bot))
