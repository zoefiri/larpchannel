import discord
import time
import json
import sys
import os
from discord.ext import commands
from discord.ext.tasks import loop

class invisibility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invis_msgs = {}
        self.bot.invis_msgs = self.invis_msgs
        if os.path.isfile('persist/invis.json'):
            self.invis = {}
            invis_buffer = json.load(open('persist/invis.json', 'r'))
            for key in invis_buffer:
                self.invis[int(key)] = invis_buffer[key]
        else:
            self.invis = {}
            json.dump(self.invis, open('persist/invis.json', 'w'))

    # sets a user's own invis
    @commands.command()
    async def invis(self, ctx, arg):
        user_id = str(ctx.author.id)
        if int(arg) not in range(15,201):
            await ctx.send('sorry, 200 seconds is the max deletion period due to memory overhead. 15 is the minimum.')
        elif user_id in self.invis[ctx.guild.id] and self.invis[ctx.guild.id][user_id]['mod']:
            await ctx.send('sorry, your invisibility was mod assigned! a mod must remove this for you to change your invisibility period.')
        else:
            self.invis[ctx.guild.id][user_id] = {'time':int(arg), 'mod': False}
            json.dump(self.invis, open('persist/invis.json', 'w'))
            await ctx.send(f'your invisibility period is now set to {int(arg)}! *stay safe.*')

    # make a user visible
    @commands.command()
    async def vis(self, ctx):
        user_id = str(ctx.author.id)
        print('selfvis', self.invis_msgs)
        if user_id not in self.invis[ctx.guild.id]:
            await ctx.send('you\'re already visible!')
        elif self.invis[ctx.guild.id][user_id]['mod']:
            await ctx.send('sorry, your invisibility was mod assigned! a mod must remove this.')
        else:
            del self.invis[ctx.guild.id][user_id]
            json.dump(self.invis, open('persist/invis.json', 'w'))
            await ctx.send(f'you are now visible!')

    # sets another user's invis
    @commands.command()
    async def mod_invis(self, ctx, *args):
        user_id = str(ctx.message.mentions[0].id)
        if len(args) > 2 or len(ctx.message.mentions) > 1:
            await ctx.send('sorry, it looks like you did something wrong! please refer to the help.')
        elif int(args[1]) not in range(15, 201):
            await ctx.send('sorry, 200 seconds is the max deletion period due to memory overhead. 15 is the minimum.')
        else:
            self.invis[ctx.guild.id][user_id] = {'time':int(args[1]), 'mod': False}
            json.dump(self.invis, open('persist/invis.json', 'w'))
            await ctx.send(f'{ctx.message.mentions[0].name}\'s invisibility period is now set to {int(args[1])}')

    # make a user visible (mod)
    @commands.command()
    async def mod_vis(self, ctx):
        user_id = str(ctx.message.mentions[0].id)
        if len(ctx.message.mentions) > 1:
            await ctx.send('sorry, it looks like you did something wrong! please refer to the help.')
        if user_id not in self.invis[ctx.guild.id]:
            await ctx.send('{ctx.message.mentions[0].name} is already visible!')
        else:
            del self.invis[ctx.guild.id][user_id]
            await ctx.send(f'{ctx.message.mentions[0].name} are now visible!')
            json.dump(self.invis, open('persist/invis.json', 'w'))

    # invisibility recorder
    @commands.Cog.listener('on_message')
    async def invis_record(self, message):
        user_id = str(message.author.id)
        if user_id in self.invis[message.guild.id]:
            expire = time.time()+self.invis[message.guild.id][user_id]['time']
            while expire in self.invis_msgs:
                expire += 0.0001
            self.invis_msgs[expire] = message

    # invisibility enforcer
    @loop(seconds=2.0)
    async def invis_enforce(bot):
        try:
            now = time.time()
            deleted = []
            print('botvis', bot.invis_msgs)
            for message_expiry in bot.invis_msgs:
                if message_expiry <= now:
                    print('MESSAGE EXPIRY!')
                    await bot.invis_msgs[message_expiry].delete()
                    deleted.append(message_expiry)
            for message_expiry in deleted:
                del bot.invis_msgs[message_expiry]

        except Exception as e:
            print(e)
            print(sys.exc_info()[-1].tb_lineno)

    # fill guild IDs out
    @commands.Cog.listener('on_ready')
    async def guild_id_fill(self):
        for guild in self.bot.guilds:
            if guild.id not in self.invis:
                self.invis[guild.id] = {}
                print('guild added to invis')
        json.dump(self.invis, open('persist/invis.json', 'w'))
        self.bot.invis = self.invis

def setup(client):
    invisibility.invis_enforce.start(client)
    client.add_cog(invisibility(client))
