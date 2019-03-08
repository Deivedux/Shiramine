import discord
import sqlite3
import datetime
import json
import aiohttp
import urllib
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

def check_perms(guild, author, member, role_perm):
	highest_role = None
	for role in author.roles:
		if role != guild.default_role and role.permissions == role_perm or role.permissions.administrator:
			highest_role = role
			break

	if ((highest_role != None and highest_role > member.top_role) or author == guild.owner) and author != member:
		return True
	else:
		return False

def dm_member(method, guild, moderator, reason):
	embed = discord.Embed(title = get_lang(guild, method), color = 0xFFFF00)
	embed.set_thumbnail(url = guild.icon_url)
	embed.add_field(name = get_lang(guild, 'ADMINISTRATION_dm_guild'), value = str(guild), inline = True)
	embed.add_field(name = get_lang(guild, 'ADMINISTRATION_dm_moderator'), value = str(moderator), inline = True)
	if reason:
		embed.add_field(name = get_lang(guild, 'ADMINISTRATION_method_reason'), value = reason, inline = False)

	return embed

def member_action_confirm(guild, method, member, reason):
	embed = discord.Embed(color = 0xFFFF00)
	embed.set_author(name = get_lang(guild, method), icon_url = member.avatar_url)
	embed.add_field(name = get_lang(guild, 'ADMINISTRATION_method_member_name'), value = str(member), inline = True)
	embed.add_field(name = get_lang(guild, 'ADMINISTRATION_method_member_id'), value = str(member.id), inline = True)
	if reason:
		embed.add_field(name = get_lang(guild, 'ADMINISTRATION_method_reason'), value = reason, inline = False)

	return embed

class Administration(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if isinstance(message.channel, discord.TextChannel) and not message.author.bot and message.attachments and not message.channel.is_nsfw() and 'img_filter' in server_config[message.guild.id].keys() and message.guild.me.permissions_in(message.channel).manage_messages:
			del_msg = False
			for attachment in message.attachments:
				if attachment.url.lower().endswith(('.jpg', '.png', '.bmp', '.gif', '.webp')):
					async with aiohttp.ClientSession() as session:
						async with session.get('https://www.moderatecontent.com/api/v2?' + urllib.parse.urlencode({'key': config['moderatecontent_api'], 'url': attachment.url})) as response:
							response_json = await response.json()

					if round(response_json['predictions']['adult']) >= server_config[message.guild.id]['img_filter']:
						del_msg = True
						break

			if del_msg == True:
				await message.delete()
				await message.channel.send(embed = discord.Embed(title = get_lang(message.guild, 'ADMINISTRATION_imgfilter_deleted_title'), description = get_lang(message.guild, 'ADMINISTRATION_imgfilter_deleted_description').format(message.author.mention, str(round(response_json['predictions']['adult']))), color = 0xFF0000))

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if not member.bot and server_config[member.guild.id]['member_persistence'] == 1 and (len(member.roles) > 1 or member.nick):
			c.execute("INSERT INTO MemberPersistence (Guild, User" + (', Nickname' if member.nick else '') + (', Roles' if len(member.roles) > 1 else '') + ") VALUES (" + str(member.guild.id) + ", " + str(member.id) + (", '" + member.nick.replace('\'', '\'\'') + "'" if member.nick else "") + (", '" + "|".join([str(role.id) for role in member.roles if role != member.guild.default_role]) + "'" if len(member.roles) > 1 else "") + ")")
			conn.commit()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if not member.bot and server_config[member.guild.id]['member_persistence'] == 1:
			try:
				db_response = c.execute("SELECT Nickname, Roles FROM MemberPersistence WHERE Guild = " + str(member.guild.id) + " AND User = " + str(member.id)).fetchall()[-1]
			except:
				return

			if db_response:
				nickname = db_response[0]
				roles = list()
				if db_response[1]:
					for i in db_response[1].split('|'):
						role = member.guild.get_role(int(i))
						if role and role < member.guild.me.top_role:
							roles.append(role)

				if nickname and len(roles) == 0:
					await member.edit(nick = nickname)
				elif not nickname and len(roles) > 0:
					await member.edit(roles = roles)
				elif nickname and len(roles) > 0:
					await member.edit(nick = nickname, roles = roles)

				c.execute("DELETE FROM MemberPersistence WHERE Guild = " + str(member.guild.id) + " AND User = " + str(member.id))
				conn.commit()

	@commands.command()
	@commands.guild_only()
	async def prefix(self, ctx, prefix = None):
		if not prefix:
			try:
				guild_prefix = server_config[ctx.guild.id]['prefix']
			except:
				guild_prefix = config['default_prefix']

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_prefix_current').format(guild_prefix), color = 0x00FF00))
		elif ctx.author.guild_permissions.manage_guild:
			c.execute("UPDATE ServerConfig SET Prefix = '" + prefix.replace('\'', '\'\'') + "' WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['prefix'] = prefix

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_prefix_update').format(prefix), color = 0x00FF00))

	@commands.command(aliases = ['k'])
	@commands.has_permissions(kick_members = True)
	async def kick(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.kick_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_kick_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, discord.Permissions.kick_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_kick_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member('ADMINISTRATION_dm_kicked', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.kick(reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.guild, 'ADMINISTRATION_method_feedback_kicked', member, reason))

	@commands.command(aliases = ['sb'])
	@commands.has_permissions(kick_members = True, manage_messages = True)
	async def softban(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.ban_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_sb_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, discord.Permissions.kick_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_sb_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member(ctx.guild, 'ADMINISTRATION_dm_softbanned', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.ban(delete_message_days = 1, reason = reason)
			await member.unban(reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.guild, 'ADMINISTRATION_method_feedback_softbanned', member, reason))

	@commands.command(aliases = ['b'])
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx, member: discord.Member, *, reason = None):
		if not ctx.guild.me.guild_permissions.ban_members:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_ban_me_noperms'), color = 0xFF0000))

		if not check_perms(ctx.guild, ctx.author, member, discord.Permissions.ban_members):

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_ban_author_noperms'), color = 0xFF0000))

		else:

			try:
				await member.send(embed = dm_member(ctx.guild, 'ADMINISTRATION_dm_banned', ctx.guild, ctx.author, reason))
			except:
				pass

			await member.ban(delete_message_days = 7, reason = reason)

			await ctx.send(embed = member_action_confirm(ctx.guild, 'ADMINISTRATION_method_feedback_banned', member, reason))

	@commands.command()
	@commands.guild_only()
	async def prune(self, ctx, msgs: int = 99):
		if ctx.author.permissions_in(ctx.channel).manage_messages:
			messages = list()
			if msgs > 99:
				msgs = 99

			async for msg in ctx.channel.history(limit = msgs, before = ctx.message):
				if (datetime.datetime.utcnow() - msg.created_at).total_seconds() < 604800:
					messages.append(msg)
				else:
					break
			messages.append(ctx.message)

			await ctx.channel.delete_messages(messages)

	@commands.command()
	@commands.guild_only()
	async def lsar(self, ctx):
		db_response = c.execute("SELECT Role FROM SelfAssignableRoles WHERE Guild = " + str(ctx.guild.id)).fetchall()
		roles = list()
		purge = False
		for i in db_response:
			role = ctx.guild.get_role(i[0])
			if role:
				roles.append(role)
			else:
				purge = True
				c.execute("DELETE FROM SelfAssignableRoles WHERE Role = " + str(i[0]))
				roles.append(str(i[0]) + ' - deleted role')

		if purge == True:
			conn.commit()

		await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_list'), description = '\n'.join([str(role) for role in roles]), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_roles = True)
	async def asar(self, ctx, *, role: discord.Role):
		roles = c.execute("SELECT Role FROM SelfAssignableRoles WHERE Guild = " + str(ctx.guild.id)).fetchall()
		if len(roles) == 10:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_add_nolimit'), color = 0xFF0000))
		elif role.id in [role[0] for role in roles]:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_add_fail').format(role.mention), color = 0xFF0000))
		else:
			c.execute("INSERT INTO SelfAssignableRoles VALUES (" + str(ctx.guild.id) + ", " + str(role.id) + ")")
			conn.commit()

			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_add_success').format(role.mention), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_roles = True)
	async def rsar(self, ctx, *, role: discord.Role):
		conf = c.execute("SELECT * FROM SelfAssignableRoles WHERE Role = " + str(role.id)).fetchone()
		if not conf:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_delete_fail').format(role.mention), color = 0xFF0000))
		else:
			c.execute("DELETE FROM SelfAssignableRoles WHERE Role = " + str(role.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_delete_success').format(role.mention), color = 0x00FF00))

	@commands.command(aliases = ['gr'])
	@commands.guild_only()
	async def giverole(self, ctx, *, role: discord.Role):
		conf = c.execute("SELECT * FROM SelfAssignableRoles WHERE Role = " + str(role.id)).fetchone()
		if not conf:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_notinlist'), color = 0xFF0000))
		else:
			try:
				await ctx.author.add_roles(role)
			except:
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_give_fail'), color = 0xFF0000))
			else:
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_give_success').format(role.mention), color = 0x00FF00))

	@commands.command(aliases = ['rr'])
	@commands.guild_only()
	async def removerole(self, ctx, *, role: discord.Role):
		conf = c.execute("SELECT * FROM SelfAssignableRoles WHERE Role = " + str(role.id)).fetchone()
		if not conf:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_notinlist'), color = 0xFF0000))
		else:
			try:
				await ctx.author.remove_roles(role)
			except:
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_remove_fail'), color = 0xFF0000))
			else:
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_selfassign_remove_success').format(role.mention), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def imgfilter(self, ctx, level: int = None):
		if not config['moderatecontent_api']:
			return await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_imgfilter_nokey'), color = 0xFF0000))

		if not level:

			if 'img_filter' not in server_config[ctx.guild.id].keys():
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_imgfilter_disable_fail'), color = 0xFF0000))
			else:
				c.execute("UPDATE ServerConfig SET ImgFilter = NULL WHERE Guild = " + str(ctx.guild.id))
				conn.commit()
				del server_config[ctx.guild.id]['img_filter']
				await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_imgfilter_disable_success'), color = 0x00FF00))

		else:

			if level > 100:
				level = 100

			c.execute("UPDATE ServerConfig SET ImgFilter = " + str(level) + " WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['img_filter'] = level
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_imgfilter_enable').format(str(level)), color = 0x00FF00))

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def memberpersistence(self, ctx):
		if server_config[ctx.guild.id]['member_persistence'] == 0:
			c.execute("UPDATE ServerConfig SET MemberPersistence = 1 WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['member_persistence'] = 1
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_memberpersistence_enabled'), color = 0x00FF00))
		else:
			c.execute("UPDATE ServerConfig SET MemberPersistence = 0 WHERE Guild = " + str(ctx.guild.id))
			conn.commit()
			server_config[ctx.guild.id]['member_persistence'] = 0
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ADMINISTRATION_memberpersistence_disabled'), color = 0x00FF00))


def setup(bot):
	bot.add_cog(Administration(bot))
