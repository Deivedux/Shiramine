import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class Administration:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def prefix(self, ctx, prefix = None):
		if not prefix:
			try:
				guild_prefix = server_config[ctx.guild.id]['prefix']
			except:
				guild_prefix = config['default_prefix']

			await ctx.send(content = get_lang(ctx)['ADMINISTRATION_prefix_current'].format(guild_prefix))
		elif ctx.author.guild_permissions.manage_guild:
			c.execute("UPDATE ServerConfig SET Prefix = '" + prefix.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['prefix'] = prefix

			await ctx.send(content = get_lang(ctx)['ADMINISTRATION_prefix_update'].format(prefix))


def setup(bot):
	bot.add_cog(Administration(bot))
