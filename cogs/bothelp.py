import discord
import time
import json
import os
from discord.ext import commands

class bothelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis
        if os.path.isfile('persist/help.json'):
            self.help_txt = json.load(open('persist/help.json', 'r'))
        else:
            self.help_txt = {'cogs':{}, 'commands':{}}
            json.dump(self.help_txt, open('persist/help.json', 'w'))

    # Fill out help dict
    @commands.Cog.listener('on_ready')
    async def help_fill(self):
        for cog in self.bot.cogs:
            if not cog in self.help_txt['cogs']:
                cog_commands = []
                for cog_command in self.bot.cogs[cog].get_commands():
                    cog_commands.append(cog_command.name)
                self.help_txt['cogs'][cog] = {'title': cog, 'info': '', 'prefix': '', 'commands': cog_commands}
        for command in self.bot.commands:
            if not command.name in self.help_txt['commands']:
                self.help_txt['commands'][command.name] = {'title': command.name, 'info': '', 'prefix': '', 'example': '',
                                                           'usage': '', 'cog': command.cog.qualified_name}
                self.help_txt['cogs'][command.cog.qualified_name]['commands'].append(command.name)
        json.dump(self.help_txt, open('persist/help.json', 'w'))

    # help command
    @commands.command()
    async def help(self, ctx, *args):
        if len(args) == 0:
            embed = discord.Embed(title = "Help", description = ("Hello! Welcome to the bot's help, here's a list of modules. To get info for a module simply type:\n"+
                                                                 "`+help <module/command>`\n"+
                                                                 "`+help rng` or `+help tarot`"), color = 0xfad037)
            for cog in self.help_txt['cogs']:
                inline = True if len(self.help_txt['cogs'][cog]['info']) < 120 else False
                embed.add_field(name=self.help_txt['cogs'][cog]['title'], value=self.help_txt['cogs'][cog]['info'], inline=inline)

        elif args[0].lower() in self.help_txt['cogs']:
            help_txt = self.help_txt['cogs'][args[0].lower()]
            command_list = ''
            for command_name in help_txt['commands']:
                command_list += f'{command_name}\n'

            embed = discord.Embed(title = help_txt['title'], description = help_txt['info'], color = 0xfad037)
            embed.add_field(name = 'commands', value = command_list, inline=False)

        elif args[0].lower() in self.help_txt['commands']:
            help_txt = self.help_txt['commands'][args[0].lower()]

            embed = discord.Embed(title = help_txt['title'], description = help_txt['info'], color = 0xfad037)
            embed.add_field(name = 'example', value = help_txt['example'], inline=False)
            embed.add_field(name = 'usage', value = help_txt['usage'], inline=False)

        await ctx.send(embed=embed)

def setup(client):
    client.remove_command('help')
    client.add_cog(bothelp(client))
