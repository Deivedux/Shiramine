import discord
import sqlite3
import datetime
import time
import random
from discord.ext import commands
from cogs.ObjectCache import response_string
from cogs.ObjectCache import get_lang
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import start_time

conn = sqlite3.connect('configs/Database.db')
c = conn.cursor()

class Utility(commands.Cog):
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

	@commands.command()
	async def stats(self, ctx):
		seconds = time.time() - start_time
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)

		embed = discord.Embed(color = 0x00FF00)
		embed.set_author(name = self.bot.user.name, icon_url = self.bot.user.avatar_url_as(size = 128))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_stats_uptime'), value = str(int(days)) + ' days\n' + str(int(hours)) + ' hours\n' + str(int(minutes)) + ' minutes')
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_stats_owners'), value = ('\n'.join(config['owner_ids']) if len(config['owner_ids']) > 0 else get_lang(ctx.guild, 'HELP_permission_none')))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_stats_presence'), value = str(len(self.bot.guilds)) + ' servers')
		await ctx.send(embed = embed)

	@commands.command()
	async def ping(self, ctx):
		now = time.time()
		msg = await ctx.send(content = ':ping_pong:')
		ping = (time.time() - now) * 1000
		await msg.edit(content = None, embed = discord.Embed(description = ':ping_pong: ' + str(round(ping)) + 'ms', color = 0x00FF00))

	@commands.command(aliases = ['uinfo'])
	async def userinfo(self, ctx, *, member: discord.Member = None):
		if not member:
			member = ctx.author

		embed = discord.Embed(title = get_lang(ctx.guild, 'UTILITY_userinfo_about'), color = 0x00FF00)
		embed.set_thumbnail(url = member.avatar_url_as(size = 128))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_id'), value = str(member.id))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_userinfo_username'), value = str(member))
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

	@commands.command(aliases = ['sinfo'])
	@commands.guild_only()
	async def serverinfo(self, ctx):
		def guild_check(check):
			pick_one = {
				'disabled': 'UTILITY_serverinfo_contentfilter_disabled',
				'no_role': 'UTILITY_serverinfo_contentfilter_noroles',
				'all_members': 'UTILITY_serverinfo_contentfilter_enabled',
				'none': 'UTILITY_serverinfo_verificationlevel_none',
				'low': 'UTILITY_serverinfo_verificationlevel_low',
				'medium': 'UTILITY_serverinfo_verificationlevel_medium',
				'high': 'UTILITY_serverinfo_verificationlevel_high',
				'extreme': 'UTILITY_serverinfo_verificationlevel_extreme',
				'1': 'UTILITY_serverinfo_2fa_enabled',
				'0': 'UTILITY_serverinfo_2fa_disabled'
			}
			return pick_one[str(check)]

		embed = discord.Embed(title = str(ctx.guild), color = 0x00FF00)
		embed.set_thumbnail(url = ctx.guild.icon_url)
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_id'), value = str(ctx.guild.id))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_owner'), value = str(ctx.guild.owner))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_createdat'), value = str(ctx.guild.created_at))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_2fa'), value = get_lang(ctx.guild, guild_check(ctx.guild.mfa_level)))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_contentfilter'), value = get_lang(ctx.guild, guild_check(ctx.guild.explicit_content_filter)))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_verificationlevel'), value = get_lang(ctx.guild, guild_check(ctx.guild.verification_level)))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_members'), value = str(ctx.guild.member_count))
		embed.add_field(name = get_lang(ctx.guild, 'UTILITY_serverinfo_channels_string'), value = get_lang(ctx.guild, 'UTILITY_serverinfo_channels_response').format(str(len(ctx.guild.text_channels)), str(len(ctx.guild.voice_channels))))

		await ctx.send(embed = embed)

	@commands.command()
	@commands.cooldown(2, 10, type = commands.BucketType.user)
	async def lookup(self, ctx, code):
		try:
			invite = await self.bot.get_invite(code)
		except discord.NotFound:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'UTILITY_lookup_fail'), color = 0xFF0000))
		else:
			def chan_type(channel):
				if isinstance(channel, discord.PartialInviteChannel):
					if channel.type == discord.ChannelType.text:
						return '#'
					elif channel.type == discord.ChannelType.voice:
						return '\\🔊'
					else:
						return ''
				else:
					if isinstance(channel, discord.TextChannel):
						return '#'
					elif isinstance(channel, discord.VoiceChannel):
						return '\\🔊'
					else:
						return ''

			desc = '• ' + get_lang(ctx.guild, 'UTILITY_lookup_server') + ': **' + str(invite.guild) + '** (' + str(invite.guild.id) + ')\n• ' + get_lang(ctx.guild, 'UTILITY_lookup_channel') + ': **' + chan_type(invite.channel) + str(invite.channel) + '** (' + str(invite.channel.id) + ')\n• ' + get_lang(ctx.guild, 'UTILITY_lookup_inviter') + ': **' + str(invite.inviter) + '**' + (' (' + str(invite.inviter.id) + ')' if invite.inviter else '') + '\n\n• ' + get_lang(ctx.guild, 'UTILITY_lookup_invitecode') + ': **' + invite.code + '**' + ('\n• ' + get_lang(ctx.guild, 'UTILITY_lookup_features') + ': ' + ', '.join(['**' + str(feature) + '**' for feature in invite.guild.features]) if len(invite.guild.features) > 0 else '') + '\n• ' + get_lang(ctx.guild, 'UTILITY_lookup_activemembers') + ': **' + str(invite.approximate_presence_count) + '** / **' + str(invite.approximate_member_count) + '**'
			embed = discord.Embed(title = get_lang(ctx.guild, 'UTILITY_lookup_about'), description = desc, color = 0x00FF00)
			embed.set_thumbnail(url = invite.guild.icon_url_as(size = 128))
			await ctx.send(embed = embed)

	@commands.command()
	@commands.guild_only()
	async def raffle(self, ctx, *, role: discord.Role = None):
		if not role:
			member = random.choice([member for member in ctx.guild.members if not member.bot])
		else:
			member = random.choice([member for member in role.members if not member.bot])

		await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'UTILITY_raffle_string'), description = member.mention + ' (' + str(member) + ')', color = 0x00FF00))


def setup(bot):
	bot.add_cog(Utility(bot))
