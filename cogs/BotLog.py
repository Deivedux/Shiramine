import discord
import json
import asyncio
import aiohttp
from discord.ext import commands
from cogs.ObjectCache import config

webhook_url = config['botlog_webhook_url']

class BotLog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_shard_ready(self, shard_id):
		async with aiohttp.ClientSession() as session:
			webhook = discord.Webhook.from_url(webhook_url, adapter = discord.AsyncWebhookAdapter(session))
			await webhook.send(content = ':ballot_box_with_check: **Shard #' + str(shard_id) + ' ready.**')

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		bots = [member for member in guild.members if member.bot]
		async with aiohttp.ClientSession() as session:
			webhook = discord.Webhook.from_url(webhook_url, adapter = discord.AsyncWebhookAdapter(session))
			await webhook.send(content = ':inbox_tray: **Guild Added** `' + guild.name.strip('`') + '` (`' + str(guild.id) + '`)\n  Total: **' + str(guild.member_count) + '** | Users: **' + str(guild.member_count - len(bots)) + '** | Bots: **' + str(len(bots)) + '**')

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		bots = [member for member in guild.members if member.bot]
		async with aiohttp.ClientSession() as session:
			webhook = discord.Webhook.from_url(webhook_url, adapter = discord.AsyncWebhookAdapter(session))
			await webhook.send(content = ':outbox_tray: **Guild Removed** `' + guild.name.strip('`') + '` (`' + str(guild.id) + '`)\n  Total: **' + str(guild.member_count) + '** | Users: **' + str(guild.member_count - len(bots)) + '** | Bots: **' + str(len(bots)) + '**')


def setup(bot):
	bot.add_cog(BotLog(bot))
