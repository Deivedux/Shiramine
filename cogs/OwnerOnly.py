import discord
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import get_lang

def is_owner(ctx):
	return ctx.author.id in config['owner_ids']

class OwnerOnly(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.check(is_owner)
	async def leave(self, ctx, guild: discord.Guild = None):
		if not guild:
			guild = ctx.guild

		await guild.leave()
		await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'OWNERONLY_leave'), color = 0x00FF00))

	@commands.command()
	@commands.check(is_owner)
	async def shutdown(self, ctx):
		await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'OWNERONLY_shutdown'), color = 0x00FF00))
		await self.bot.logout()


def setup(bot):
	bot.add_cog(OwnerOnly(bot))
