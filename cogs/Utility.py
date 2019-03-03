import discord
import sqlite3
import datetime
from discord.ext import commands
from cogs.ObjectCache import response_string
from cogs.ObjectCache import get_lang
from cogs.ObjectCache import server_config

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class Utility:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def languages(self, ctx):
		langs = list()
		for i in response_string.keys():
			langs.append(i.capitalize())
		langs.sort()

		embed = discord.Embed(title = get_lang(ctx.guild, 'UTILITY_language_list'), description = '\n'.join(['• ' + i for i in langs]), color = 0x00FF00)
		embed.set_footer(text = get_lang(ctx.guild, 'UTILITY_language_footer'))
		await ctx.send(embed = embed)

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def setlang(self, ctx, lang):
		if lang.lower() not in response_string.keys():
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'UTILITY_language_set_fail'), color = 0xFF0000))
		else:
			c.execute("UPDATE ServerConfig SET Language = '" + lang.lower() + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['language'] = lang.lower()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'UTILITY_language_set_success'), color = 0x00FF00))

	@commands.command(aliases = ['uinfo'])
	async def userinfo(self, ctx, *, member: discord.Member = None):
		if not member:
			member = ctx.author

		embed = discord.Embed(color = 0x00FF00)
		embed.set_author(name = str(member), icon_url = member.avatar_url)
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_id'), value = str(member.id))
		if member.nick:
			embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_nickname'), value = member.nick)
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_joined_discord'), value = str(member.created_at))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_joined_guild'), value = str(member.joined_at))
		if len(member.roles) > 1:
			embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_roles'), value = ', '.join(['`' + str(role) + '`' for role in member.roles if role != ctx.guild.default_role]), inline = False)

		await ctx.send(embed = embed)

	@commands.command(aliases = ['av'])
	async def avatar(self, ctx, *, member: discord.Member = None):
		if not member:
			member = ctx.author

		embed = discord.Embed(title = str(member), color = 0x00FF00)
		embed.set_image(url = member.avatar_url)

		await ctx.send(embed = embed)

	'''@commands.command(aliases = ['sinfo'])
	@commands.guild_only()
	async def serverinfo(self, ctx):
		'''


def setup(bot):
	bot.add_cog(Utility(bot))
