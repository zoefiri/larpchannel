import discord
import commands
import os
import time
import glob
from random import seed, randint
from quotes import retrieve_quotes, find_quotes
from driv import get_rand_card

token = 'NjY2Mjg5ODE1ODE3Mjg5NzM4.XhyCyg.L30qnyCQ8wYG-k92ZXLy_qSh86Y'
client = discord.Client()
seed(time.time())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'we\'re on servers:')
    for guild in client.guilds:
        print(f'\t{guild}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content == 'yugioh!' or message.content == 'Yugioh!':
        print("FUCK")
        get_rand_card()
        await message.channel.send(file=discord.File('card.png'))
    elif message.content[0:7] == 'x!tarot' or message.content[0:7] == 'X!tarot':
        cards = glob.glob('cards/*')
        await message.channel.send(file=discord.File(cards[randint(0,len(cards)-1)]))
    elif message.content[0:3] == 'bbq':
        bbq=['No.', 'Mote it be.', 'Never.', 'Yes.', 'I will it.', 'Absolutely not.', 'Yes, of course.', 'No', 'That will never happen.']
        await message.channel.send(bbq[randint(0,len(bbq)-1)])
    else:
        cmd_list = vars(commands.cmds)
        cmd_names = list(filter(lambda x: x[0] != '_' , cmd_list.keys()))
        for command in cmd_names:
            if cmd_list[command].command_text == message.content:
                cmd_list[command].action()
                return
            return

client.run(token)

