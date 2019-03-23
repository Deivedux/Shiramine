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
	async def setstatus(self, ctx, status_type: int, *, status):
		status = status.split(' | ')

		if len(status) == 2:
			await self.bot.change_presence(activity = discord.Activity(name = status[0], type = status_type, url = status[1]))
		else:
			await self.bot.change_presence(activity = discord.Activity(name = status[0], type = status_type))

		await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'OWNERONLY_status'), color = 0x00FF00))

	@commands.command()
	@commands.check(is_owner)
	async def leaveserver(self, ctx, guild: discord.Guild = None):
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
