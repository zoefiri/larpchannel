import discord
import signal
import redis
import time
import json
import sys
import os
from discord.ext import commands
from discord.ext.tasks import loop

token = ''
if os.path.isfile('persist/token.json'):
    token = json.load(open('persist/token.json', 'r'))['token']
else:
    print('rlease put bot token into persist/token.json')
    json.dump({'token':''}, open('persist/token.json', 'w'))
    exit()

client = discord.Client()
bot = commands.Bot(command_prefix='+')
redis_client = redis.Redis(host='localhost',
                           port='6379',
                           decode_responses = True)
bot.redis = redis_client

exts = ['cogs.perms',
        'cogs.bothelp',
        'cogs.rng',
        'cogs.quotes',
        'cogs.timed_roles']

for ext in exts:
    bot.load_extension(ext)

@bot.event
async def on_ready():
    print(bot.get_cog("quotes").__cog_listeners__ )
    print('reddy\'')

@bot.check
def check_perms(ctx):
    command = ctx.command.name
    user = ctx.author.id
    guild = ctx.guild.id
    cog = ctx.cog.qualified_name
    permscope = bot.perms[guild]
    roles = []
    for role in ctx.author.roles:
        roles.append(role.name)

    if user == ctx.guild.owner_id or user == 132620792818171905: return True

    permscope = bot.perms[guild]['users']
    if user and str(user) in permscope:
        print('PERMSINFO')
        if command in permscope[str(user)]: return permscope[str(user)][command]
        elif cog in permscope[str(user)]: return permscope[str(user)][cog]
        elif '*' in permscope[str(user)]: return permscope[str(user)]['*']

    permscope = bot.perms[guild]['roles']
    rolescope_list = set(roles).intersection(permscope)
    for role in rolescope_list:
        role = permscope[role]
        if command in role: return role[command]
        elif cog in role: return role[cog]

    permscope = bot.perms[guild]['commands']
    if command and command in permscope: return permscope[command]

    permscope = bot.perms[guild]['cogs']
    if cog and cog in permscope: return permscope[cog]

bot.run(token)
