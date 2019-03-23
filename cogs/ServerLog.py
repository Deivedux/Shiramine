import discord
import sqlite3
import datetime
from discord.ext import commands
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class ServerLog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if not message.author.bot and 'server_log' in server_config[message.guild.id].keys():
			channel = self.bot.get_channel(server_config[message.guild.id]['server_log'])
			if channel:
				embed = discord.Embed(title = get_lang(message.guild, 'ADMINISTRATION_serverlog_msgdelete'), description = message.content, color = 0xFFFF00, timestamp = datetime.datetime.utcnow())
				embed.set_footer(icon_url = message.author.avatar_url_as(size = 128), text = str(message.author) + ' (' + str(message.author.id) + ')')
				await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.author.bot and 'server_log' in server_config[after.guild.id].keys() and before.content != after.content:
			channel = self.bot.get_channel(server_config[after.guild.id]['server_log'])
			if channel:
				embed = discord.Embed(title = get_lang(after.guild, 'ADMINISTRATION_serverlog_msgedit_title'), color = 0xFFFF00, timestamp = datetime.datetime.utcnow())
				embed.add_field(name = get_lang(after.guild, 'ADMINISTRATION_serverlog_before'), value = before.content)
				embed.add_field(name = get_lang(after.guild, 'ADMINISTRATION_serverlog_after'), value = after.content)
				embed.set_footer(icon_url = after.author.avatar_url_as(size = 128), text = str(after.author) + ' (' + str(after.author.id) + ')')
				await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if 'server_log' in server_config[member.guild.id].keys():
			channel = self.bot.get_channel(server_config[member.guild.id]['server_log'])
			if channel:
				embed = discord.Embed(title = get_lang(member.guild, 'ADMINISTRATION_serverlog_member_join'), description = get_lang(member.guild, 'ADMINISTRATION_serverlog_member_members').format(str(member.guild.member_count)), color = 0x00FF00, timestamp = datetime.datetime.utcnow())
				embed.set_footer(icon_url = member.avatar_url_as(size = 128), text = str(member) + ' (' + str(member.id) + ')')
				await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if 'server_log' in server_config[member.guild.id].keys():
			channel = self.bot.get_channel(server_config[member.guild.id]['server_log'])
			if channel:
				embed = discord.Embed(title = get_lang(member.guild, 'ADMINISTRATION_serverlog_member_leave'), description = get_lang(member.guild, 'ADMINISTRATION_serverlog_member_members').format(str(member.guild.member_count)), color = 0xFF0000, timestamp = datetime.datetime.utcnow())
				embed.set_footer(icon_url = member.avatar_url_as(size = 128), text = str(member) + ' (' + str(member.id) + ')')
				await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if 'server_log' in server_config[after.guild.id].keys() and before.display_name != after.display_name:
			channel = self.bot.get_channel(server_config[after.guild.id]['server_log'])
			if channel:
				embed = discord.Embed(title = get_lang(after.guild, 'ADMINISTRATION_serverlog_member_update'), color = 0x8E44AD, timestamp = datetime.datetime.utcnow())
				embed.add_field(name = get_lang(after.guild, 'ADMINISTRATION_serverlog_before'), value = before.display_name)
				embed.add_field(name = get_lang(after.guild, 'ADMINISTRATION_serverlog_after'), value = after.display_name)
				embed.set_footer(icon_url = after.avatar_url_as(size = 128), text = str(after) + ' (' + str(after.id) + ')')
				await channel.send(embed = embed)


def setup(bot):
	bot.add_cog(ServerLog(bot))
