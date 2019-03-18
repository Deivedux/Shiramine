import discord
import sqlite3
import datetime
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import get_lang

conn = sqlite3.connect('configs/Database.db', detect_types = sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

def is_owner(ctx):
	return ctx.author.id in config['owner_ids']

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases = ['cur'])
	async def currency(self, ctx, user: discord.User = None):
		if not user:
			user = ctx.author

		db_response = c.execute("SELECT Amount FROM Currency WHERE User = " + str(user.id)).fetchone()
		if not db_response:
			c.execute("INSERT INTO Currency (User, Amount) VALUES (" + str(user.id) + ", 0)")
			conn.commit()
			db_response = c.execute("SELECT Amount FROM Currency WHERE User = " + str(user.id)).fetchone()

		await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_currency').format(user.mention, str(db_response[0])), color = 0x00FF00))

	@commands.command()
	@commands.check(is_owner)
	async def award(self, ctx, user_id: int, amount: int):
		user = self.bot.get_user(user_id)
		if not user:
			try:
				user = await self.bot.get_user_info(user_id)
			except discord.NotFound:
				return await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_award_nouser'), color = 0xFF0000))

		try:
			c.execute("INSERT INTO Currency (User, Amount) VALUES (" + str(user.id) + ", " + str(amount) + ")")
		except sqlite3.IntegrityError:
			c.execute("UPDATE Currency SET Amount = Amount + " + str(amount) + " WHERE User = " + str(user.id))
		conn.commit()
		await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_award_success').format(str(user), str(amount)), color = 0x00FF00))

		try:
			await user.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_award_dm').format(str(amount)), color = 0x00FF00))
		except discord.Forbidden:
			pass

	@commands.command()
	@commands.check(is_owner)
	async def take(self, ctx, user_id: int, amount: int):
		user = self.bot.get_user(user_id)
		if not user:
			try:
				user = await self.bot.get_user_info(user_id)
			except discord.NotFound:
				return await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_award_nouser'), color = 0xFF0000))

		db_response = c.execute("SELECT Amount FROM Currency WHERE User = " + str(user.id)).fetchone()
		if db_response and db_response[0] >= amount:
			c.execute("UPDATE Currency SET Amount = Amount - " + str(amount) + " WHERE User = " + str(user.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_take_success').format(str(user), str(amount)), color = 0x00FF00))
		else:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_take_fail'), color = 0xFF0000))

	@commands.command()
	async def claim(self, ctx):
		db_response = c.execute("SELECT Claimed FROM Currency WHERE User = " + str(ctx.author.id)).fetchone()
		if not db_response or (datetime.datetime.utcnow() - db_response[0]).total_seconds() > 604800:
			try:
				c.execute("INSERT INTO Currency VALUES (" + str(ctx.author.id) + ", " + str(config['claim_amount']) + ", '" + str(datetime.datetime.utcnow()) + "')")
			except sqlite3.IntegrityError:
				c.execute("UPDATE Currency SET Amount = Amount + " + str(config['claim_amount']) + ", Claimed = '" + str(datetime.datetime.utcnow()) + "' WHERE User = " + str(ctx.author.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_claim_success').format(ctx.author.mention), color = 0x00FF00))
		else:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_claim_fail'), color = 0xFF0000))

	@commands.command()
	async def give(self, ctx, user: discord.User, amount: int):
		db_response = c.execute("SELECT Amount FROM Currency WHERE User = " + str(ctx.author.id)).fetchone()
		if not db_response or amount > db_response[0] or amount < 0:
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_give_fail'), color = 0xFF0000))
		else:
			c.execute("UPDATE Currency SET Amount = Amount - " + str(amount) + " WHERE User = " + str(ctx.author.id))
			try:
				c.execute("INSERT INTO Currency (User, Amount) VALUES (" + str(user.id) + ", " + str(amount) + ")")
			except sqlite3.IntegrityError:
				c.execute("UPDATE Currency SET Amount = Amount + " + str(amount) + " WHERE User = " + str(user.id))
			conn.commit()
			await ctx.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_give_success').format(str(user), str(amount)), color = 0x00FF00))

			try:
				await user.send(embed = discord.Embed(description = get_lang(ctx.guild, 'ECONOMY_give_dm').format(str(ctx.author), str(amount)), color = 0x00FF00))
			except discord.Forbidden:
				pass

	@commands.command(aliases = ['lb'])
	async def leaderboard(self, ctx, page_number: int = 1):
		db_response = c.execute("SELECT User, Amount FROM Currency ORDER BY Amount DESC LIMIT 10 OFFSET " + str(10 * (page_number - 1))).fetchall()
		position = 10 * (page_number - 1)
		users = list()
		for i in db_response:
			position += 1
			user = self.bot.get_user(i[0])
			if user:
				user = user
			else:
				user = i[0]
			users.append('`' + str(position) + '.` ' + str(user) + ' - **' + str(i[1]) + '** currency')
		await ctx.send(embed = discord.Embed(title = get_lang(ctx.guild, 'ECONOMY_leaderboard_title'), description = '\n'.join(users), color = 0x00FF00))


def setup(bot):
	bot.add_cog(Economy(bot))
