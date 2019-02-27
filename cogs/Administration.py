import discord
import sqlite3
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

def check_perms(guild, author, member, role_perm):
	highest_role = None
	for role in author.roles:
		if role != guild.default_role and role_perm:
			highest_role = role
			break

	if highest_role != None and highest_role > member.top_role:
		return True
	else:
		return False

def dm_member(message, method, guild, moderator, reason):
	embed = discord.Embed(title = get_lang(message, method), color = 0xFFFF00)
	embed.set_thumbnail(url = guild.icon_url)
	embed.add_field(name = get_lang(message, 'ADMINISTRATION_dm_guild'), value = str(guild), inline = True)
	embed.add_field(name = get_lang(message, 'ADMINISTRATION_dm_moderator'), value = str(moderator), inline = True)
	if reason:
		embed.add_field(name = get_lang(message, 'ADMINISTRATION_method_reason'), value = reason, inline = False)

	return embed

def member_action_confirm(message, method, member, reason):
	embed = discord.Embed(title = method, color = 0xFFFF00)
	embed.set_thumbnail(url = member.avatar_url)
	embed.add_field(name = get_lang(message, 'ADMINISTRATION_method_member_name'), value = str(member), inline = True)
	embed.add_field(name = get_lang(message, 'ADMINISTRATION_method_member_id'), value = str(member.id), inline = True)
	if reason:
		embed.add_field(name = get_lang(message, 'ADMINISTRATION_method_reason'), value = reason, inline = False)

	return embed

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

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_prefix_current').format(guild_prefix), color = 0x00FF00))
		elif ctx.author.guild_permissions.manage_guild:
			c.execute("UPDATE ServerConfig SET Prefix = '" + prefix.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['prefix'] = prefix

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_prefix_update').format(prefix), color = 0x00FF00))

	@commands.command(aliases = ['k'])
	@commands.has_permissions(kick_members = True)
	async def kick(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.kick_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_kick_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, role.permissions.kick_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_kick_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member(ctx.message, 'ADMINISTRATION_dm_kicked', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.kick(reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.message, 'ADMINISTRATION_method_feedback_kicked', member, reason))

	@commands.command(aliases = ['sb'])
	@commands.has_permissions(kick_members = True, manage_messages = True)
	async def softban(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.ban_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_sb_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, role.permissions.kick_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_sb_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member(ctx.message, 'ADMINISTRATION_dm_softbanned', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.ban(delete_message_days = 1, reason = reason)
			await member.unban(reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.message, 'ADMINISTRATION_method_feedback_softbanned', member, reason))

	@commands.command(aliases = ['b'])
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.ban_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_ban_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, role.permissions.kick_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.message, 'ADMINISTRATION_ban_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member(ctx.message, 'ADMINISTRATION_dm_banned', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.ban(delete_message_days = 7, reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.message, 'ADMINISTRATION_method_feedback_banned', member, reason))

	@commands.command()
	@commands.guild_only()
	async def prune(self, ctx, msgs: int = 99):
		if ctx.author.permissions_in(ctx.channel).manage_messages:
			messages = []
			async for msg in ctx.channel.history(limit = msgs, before = ctx.message):
				messages.append(msg)
			messages.append(ctx.message)

			await ctx.channel.delete_messages(messages)


def setup(bot):
	bot.add_cog(Administration(bot))
