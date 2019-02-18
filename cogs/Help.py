import discord
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang
from collections import OrderedDict

class Help:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def help(self, ctx, command_name = None):
		try:
			guild_prefix = server_config[ctx.guild.id]['prefix']
		except:
			guild_prefix = config['default_prefix']

		with open('commands.json') as json_data:
			commands_json = json.load(json_data, object_pairs_hook = OrderedDict)

		if not command_name:

			embed = discord.Embed(title = 'Command List', color = 0x00FF00)
			embed.add_field(name = 'Help', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json if commands_json[i]['module']] == 'Help'), inline = False)
			embed.add_field(name = 'Administration', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json if commands_json[i]['module']] == 'Administration'), inline = False)
			embed.set_footer(text = get_lang(ctx)['HELP_response_footer'])

			await ctx.send(embed = embed)

		else:

			embed = discord.Embed(title = )


def setup(bot):
	bot.add_cog(Help(bot))
