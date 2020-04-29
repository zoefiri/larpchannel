import discord
import random
import threading
import time
import json
import sys
import os
from parse import parse
from recordtype import recordtype
from discord.ext import commands
from discord.ext.tasks import loop

class banner(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       bot.banner = self
       self.alternator = 1

       self.err_disabled = 'please enable banner rotation with `+toggle_banners` before using this command!'
       self.err_attachmissing = 'please send a file with your message to add as a banner, no links.'
       self.err_addarg = 'please provide a name for this banner, `.` and `/` chars ar'
       self.err_noname = 'that banner name was not found! please enter another.'
       self.err_nameused = 'that banner name is already used, please enter another.'

       if not os.path.isdir('persist/banners'):
          os.mkdir('persist/banners')
       if os.path.isfile('persist/banner.json'):
          bannerinf_buffer = json.load(open('persist/banner.json', 'r'))
          self.bannerinf = {}
          for guild_id in bannerinf_buffer:
             self.bannerinf[int(guild_id)] = bannerinf_buffer[guild_id]
       else:
          self.bannerinf = {}
          json.dump(self.bannerinf, open('persist/banner.json', 'w'))

    @commands.command()
    async def toggle_banners(self, ctx):
        disabled = 'banner rotation disabled!'
        enabled = 'banner rotation enabled!'
        if not ctx.guild.id in self.bannerinf:
            if not os.path.isdir(f'persist/banners/{ctx.guild.id}'):
                os.mkdir(f'persist/banners/{ctx.guild.id}')
            self.bannerinf[ctx.guild.id] = {"banners": [], "enabled": True}
            await ctx.send(enabled)
        elif self.bannerinf[ctx.guild.id]["enabled"]:
            self.bannerinf[ctx.guild.id]["enabled"] = False
            await ctx.send(disabled)
        else:
            self.bannerinf[ctx.guild.id]["enabled"] = True
            json.dump(self.bannerinf, open('persist/banner.json', 'w'))
            await ctx.send(enabled)

    @commands.command()
    async def add_banner(self, ctx, arg):
        if not ctx.guild.id in self.bannerinf or not self.bannerinf[ctx.guild.id]["enabled"]:
            await ctx.send(self.err_disabled)
        elif not ctx.message.attachments:
            await ctx.send(self.err_attachmissing)
        elif not arg.isalnum():
            await ctx.send(self.err_addarg)
        elif arg in self.bannerinf[ctx.guild.id]["banners"]:
            await ctx.send(self.err_nameused)
        else:
            await ctx.message.attachments[0].save(f'persist/banners/{ctx.guild.id}/{arg}', seek_begin=True, use_cached=False)
            self.bannerinf[ctx.guild.id]["banners"].append(arg)
            json.dump(self.bannerinf, open('persist/banner.json', 'w'))
            await ctx.send(f'banner saved as {arg}!')

    @commands.command()
    async def del_banner(self, ctx, arg):
        if not ctx.guild.id in self.bannerinf or not self.bannerinf[ctx.guild.id]["enabled"]:
            await ctx.send(self.err_disabled)
        elif not arg.isalnum():
            await ctx.send(self.err_addarg)
        elif not arg in self.bannerinf[ctx.guild.id]["banners"]:
            await ctx.send(self.err_noname)
        else:
            os.remove(f'persist/banners/{ctx.guild.id}/{arg}')
            self.bannerinf[ctx.guild.id]["banners"].remove(arg)
            json.dump(self.bannerinf, open('persist/banner.json', 'w'))
            await ctx.send(f'banner saved as {arg}!')

    @commands.command()
    async def ls_banner(self, ctx):
        message = ''
        for banner in self.bannerinf[ctx.guild.id]["banners"]:
            message += f'**{banner}**\n'
        await ctx.send(message)

    @commands.command()
    async def v_banner(self, ctx, arg):
        if arg in self.bannerinf[ctx.guild.id]["banners"]:
            file = discord.File(f'persist/banners/{ctx.guild.id}/{arg}', filename=(arg+".png"))
            await ctx.send(file=file)
        else:
            await ctx.send('Banner does not exist! Check +ls_banner.')


    @loop(seconds=120.0)
    async def changer(bot):
        self = bot.banner
        try:
            for guild_id in self.bannerinf:
                guild = self.bot.get_guild(guild_id)
                banner_fname=f'persist/banners/{guild_id}/{random.choice(self.bannerinf[guild_id]["banners"])}'
                bannerfile = ''
                with open(banner_fname, mode='rb') as file:
                    bannerfile = file.read()
                await guild.edit(banner=bannerfile)
            self.alternator += 1
            if self.alternator > 1000:
                self.alternator = 1
        except Exception as e:
            print(e)
            print(sys.exc_info()[-1].tb_lineno)


def setup(bot):
    banner.changer.start(bot)
    bot.add_cog(banner(bot))
