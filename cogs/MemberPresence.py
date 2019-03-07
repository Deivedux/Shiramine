import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class MemberPresence(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member):
		db_response = c.execute("SELECT GreetMsg, GreetChannel, GreetDel, GreetDmMsg, GreetDmToggle FROM ServerConfig WHERE Guild = " + str(member.guild.id)).fetchone()
		if db_response[1]:
			channel = member.guild.get_channel(db_response[1])
			if channel and member.permissions_in(channel).read_messages and member.guild.me.permissions_in(channel).send_messages:
				await channel.send(content = db_response[0].replace('&user&', member.mention).replace('&server&', str(member.guild)), delete_after = db_response[2])
		if db_response[4] == 1:
			try:
				await member.send(content = db_response[3].replace('&user&', member.name).replace('&server&', str(member.guild)))
			except discord.Forbidden:
				pass

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		db_response = c.execute("SELECT LeaveMsg, LeaveChannel, LeaveDel FROM ServerConfig WHERE Guild = " + str(member.guild.id)).fetchone()
		if db_response[1]:
			channel = member.guild.get_channel(db_response[1])
			if channel and member.permissions_in(channel).read_messages and member.guild.me.permissions_in(channel).send_messages:
				await channel.send(content = db_response[0].replace('&user&', str(member)).replace('&server&', str(member.guild)), delete_after = db_response[2])

	@commands.command()
	@commands.guild_only()
	async def greetmsg(self, ctx, *, msg = None):
		if not msg:
			db_response = c.execute("SELECT GreetMsg FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
			await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'MEMBERPRESENCE_greetmsg_currentmsg'), description = db_response[0], color = 0x00FF00))
		elif ctx.author.guild_permissions.manage_server:
			c.execute("UPDATE ServerConfig SET GreetMsg = '" + msg.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetmsg_updatemsg'), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def greetdel(self, ctx, arg: int = None):
		if not arg:
			c.execute("UPDATE ServerConfig SET GreetDel = NULL WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdel_disabled'), color = 0x00FF00))
		elif arg < 1 or arg > 120:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdel_fail'), color = 0xFF0000))
		else:
			c.execute("UPDATE ServerConfig SET GreetDel = " + str(arg) + " WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdel_enabled').format(str(arg)), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def greet(self, ctx):
		db_response = c.execute("SELECT GreetChannel FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
		if not db_response[0]:
			c.execute("UPDATE ServerConfig SET GreetChannel = " + str(ctx.channel.id) + " WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greet_enabled'), color = 0x00FF00))
		else:
			c.execute("UPDATE ServerConfig SET GreetChannel = NULL WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greet_disabled'), color = 0x00FF00))

	@commands.command()
	@commands.guild_only()
	async def leavemsg(self, ctx, *, msg = None):
		if not msg:
			db_response = c.execute("SELECT LeaveMsg FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
			await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'MEMBERPRESENCE_leavemsg_currentmsg'), description = db_response[0], color = 0x00FF00))
		elif ctx.author.guild_permissions.manage_server:
			c.execute("UPDATE ServerConfig SET LeaveMsg = '" + msg.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_leavemsg_updatemsg'), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def leavedel(self, ctx, arg: int = None):
		if not arg:
			c.execute("UPDATE ServerConfig SET LeaveDel = NULL WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_leavedel_disabled'), color = 0x00FF00))
		elif arg < 1 or arg > 120:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdel_fail'), color = 0xFF0000))
		else:
			c.execute("UPDATE ServerConfig SET LeaveDel = " + str(arg) + " WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_leavedel_enabled').format(str(arg)), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def leave(self, ctx):
		db_response = c.execute("SELECT LeaveChannel FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
		if not db_response[0]:
			c.execute("UPDATE ServerConfig SET LeaveChannel = " + str(ctx.channel.id) + " WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_leave_enabled'), color = 0x00FF00))
		else:
			c.execute("UPDATE ServerConfig SET LeaveChannel = NULL WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_leave_disabled'), color = 0x00FF00))

	@commands.command()
	@commands.guild_only()
	async def greetdmmsg(self, ctx, *, msg = None):
		if not msg:
			db_response = c.execute("SELECT GreetDmMsg FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
			await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdmmsg_currentmsg'), description = db_response[0], color = 0x00FF00))
		elif ctx.author.guild_permissions.manage_server:
			c.execute("UPDATE ServerConfig SET GreetDmMsg = '" + msg.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdmmsg_updatemsg'), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def greetdm(self, ctx):
		db_response = c.execute("SELECT GreetDmToggle FROM ServerConfig WHERE Guild = " + str(ctx.guild.id)).fetchone()
		if db_response[0] == 0:
			c.execute("UPDATE ServerConfig SET GreetDmToggle = 1 WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdm_enabled'), color = 0x00FF00))
		else:
			c.execute("UPDATE ServerConfig SET GreetDmToggle = 0 WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'MEMBERPRESENCE_greetdm_disabled'), color = 0x00FF00))


def setup(bot):
	bot.add_cog(MemberPresence(bot))
