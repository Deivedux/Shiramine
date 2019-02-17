import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

bot = commands.AutoShardedBot()
bot.remove_command('help')


bot.run()
