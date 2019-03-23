import discord
import json
from discord.ext import commands
from cogs.ObjectCache import config
from cogs.ObjectCache import server_config
from cogs.ObjectCache import get_lang
from collections import OrderedDict

with open('commands.json') as json_data:
	commands_json = json.load(json_data, object_pairs_hook = OrderedDict)

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases = ['h'])
	async def help(self, ctx, command_name = None):
		try:
			guild_prefix = server_config[ctx.guild.id]['prefix']
		except:
			guild_prefix = config['default_prefix']

		if not command_name:

			embed = discord.Embed(color = 0x00FF00)
			embed.set_author(name = self.bot.user.name, icon_url = self.bot.user.avatar_url)
			embed.add_field(name = 'Help', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json.keys() if commands_json[i]['module'] == 'Help']), inline = False)
			embed.add_field(name = 'Administration', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json.keys() if commands_json[i]['module'] == 'Administration']), inline = False)
			embed.add_field(name = 'MemberPresence', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json.keys() if commands_json[i]['module'] == 'MemberPresence']), inline = False)
			embed.add_field(name = 'Economy', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json.keys() if commands_json[i]['module'] == 'Economy']), inline = False)
			embed.add_field(name = 'Utility', value = ', '.join(['`' + guild_prefix + i + '`' for i in commands_json.keys() if commands_json[i]['module'] == 'Utility']), inline = False)
			embed.set_footer(text = get_lang(ctx.guild, 'HELP_response_footer').format(guild_prefix))

		else:

			try:
				cmd_data = commands_json[command_name.lower()]
			except:
				return await ctx.send(embed = discord.Embed(description = get_lang(ctx, 'HELP_command_notfound'), color = 0xFF0000))

			embed = discord.Embed(title = ' / '.join(['`' + guild_prefix + i + '`' for i in cmd_data['title']]), description = get_lang(ctx.guild, cmd_data['description']), color = 0x00FF00)
			embed.add_field(name = get_lang(ctx.guild, 'HELP_permission_string_user'), value = '\n'.join(['`' + get_lang(ctx.guild, i) + '`' for i in cmd_data['user_permissions']]), inline = True)
			embed.add_field(name = get_lang(ctx.guild, 'HELP_permission_string_bot'), value = '\n'.join(['`' + get_lang(ctx.guild, i) + '`' for i in cmd_data['bot_permissions']]), inline = True)
			embed.add_field(name = get_lang(ctx.guild, 'HELP_example_string'), value = ' or '.join(['`' + guild_prefix + i + '`' for i in cmd_data['examples']]), inline = False)
			embed.set_footer(text = 'Module: ' + cmd_data['module'])

		await ctx.send(embed = embed)

	@commands.command()
	async def invite(self, ctx):
		await ctx.send(embed = discord.Embed(description = '[Support Server](https://discord.gg/sbySHxA)\n[Add Me](https://discordapp.com/oauth2/authorize?client_id=' + str(self.bot.user.id) + '&scope=bot&permissions=0)\n[GitHub](https://github.com/Deivedux/Shiramine)\n[Patreon](https://www.patreon.com/QuoteBot)', color = 0x00FF00))


def setup(bot):
	bot.add_cog(Help(bot))
