import discord
import commands_old
import signal
import redis
import time
import json
import sys
import os
from discord.ext import commands
from discord.ext.tasks import loop

token = 'NjY2Mjg5ODE1ODE3Mjg5NzM4.XjRKug.hLMDddmi9mDv4wzmmE55Em4hFaw'
client = discord.Client()
bot = commands.Bot(command_prefix='+')
bot.redis = redis.Redis(host='localhost',
                        port='6379',
                        password=None)

exts = ['cogs.rng']

for ext in exts:
    bot.load_extension(ext)

cmd_globals = {
    'client': client,
    'slowed': json.load(open('ratelimit.json', 'r')),
    'responses' : json.load(open('responses.json', 'r')),
    'quote_queue' : {},
    'limited' : {},
    'role_timed': {},
    'help_info': {},
    'nums' : [],
    'limit' : 60,
    'ratelimit' : 30,
    'unltd' : False,
    'disabled': False
}
if os.path.exists('role_schedule.json'): cmd_globals['role_timed'] = json.load(open('role_schedule.json', 'r'))

@loop(seconds=1.0)
async def role_remover():
    now = time.time()
    removed = []
    print('hey')
    for temprole_key in cmd_globals['role_timed']:
        temprole = cmd_globals['role_timed'][temprole_key]
        if now-temprole['assigned'] > temprole['duration']:
            for guild in client.guilds:
                if guild.id == temprole['guild']:
                    member = guild.get_member(temprole['member'])
                    role_guild = guild
            for role in role_guild.roles:
                if role.name.lower() == temprole['role'].lower():
                    await member.remove_roles(role)
            removed.append(temprole_key)

    for temprole_key in removed:
        del cmd_globals['role_timed'][temprole_key]
        json.dump(cmd_globals['role_timed'], open('role_schedule.json', 'w'))


@client.event
async def on_ready():
    role_remover.start()

    conv_buffer = []
    for user in cmd_globals['slowed']:
        conv_buffer.append(user)
    for user in conv_buffer:
        cmd_globals['slowed'][int(user)] = cmd_globals['slowed'][user]
        del cmd_globals['slowed'][user]

    print(f'{client.user} has connected to Discord!')
    print(f'we\'re on servers:')
    for guild in client.guilds:
        print(f'\t{guild}')

cmd_list = vars(commands_old.cmds)
cmd_names = list(filter(lambda x: x[0] != '_' , cmd_list.keys()))
for command in cmd_names:
    if "command_text" in vars(cmd_list[command]):
        command_text = cmd_list[command].command_text
        if "help_text" in vars(cmd_list[command]):
            help_text = cmd_list[command].help_text
            cmd_globals['help_info'][command_text] = help_text
        else:
            cmd_globals['help_info'][command_text] = ''

@client.event
async def on_member_join(member):
    for timed_role in cmd_globals['role_timed']:
        timed_role_val = cmd_globals['role_timed'][timed_role]
        if timed_role_val['member'] == member.id and time.time()-timed_role_val['assigned'] < timed_role_val['duration']:
            for role in member.guild.roles:
                if role.name == timed_role_val['role']:
                    await member.add_roles(role)


@client.event
async def on_message(message):
    cmd_list = vars(commands_old.cmds)
    cmd_names = list(filter(lambda x: x[0] != '_' , cmd_list.keys()))
    for command in cmd_names:
        if not cmd_globals['disabled'] and not message.author.bot and message.content != '' and "command_text" in vars(cmd_list[command]) and cmd_list[command].command_text == message.content.split()[0].lower():
            await cmd_list[command].action(message, cmd_globals)
            print(f'ACTIVATED {command} text activated')
            return
        elif not cmd_globals['disabled'] and not message.author.bot and "command_text" not in vars(cmd_list[command]) and "custom_logic" in vars(cmd_list[command]):
            await cmd_list[command].action(message, cmd_globals)
    if message.author.id == 132620792818171905 and message.content == '+disable':
        if cmd_globals['disabled']: cmd_globals['disabled'] = False
        else: cmd_globals['disabled'] = True
        print('disabling', cmd_globals['disabled'])
    return


bot.run(token)
