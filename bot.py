import discord
import commands
import os
import time
import glob
import requests
from random import seed, randint
from quotes import retrieve_quotes, find_quote, add_quote
from driv import get_rand_card

token = 'NjY2Mjg5ODE1ODE3Mjg5NzM4.XieQsw.kybrZ44ct9aXvJuI1Tb-jFQIQHc'
client = discord.Client()
seed(time.time())
nums = []
quote_queue = {}
limited = {}
limit = 60
unltd = False
responses = retrieve_quotes()
ratelimit = 30

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'we\'re on servers:')
    for guild in client.guilds:
        print(f'\t{guild}')

@client.event
async def on_message(message):
    global responses
    global limited
    global nums
    global unltd
    global limit
    if message.author == client.user:
        return
    elif message.content == 'yugioh!' or message.content == 'Yugioh!':
        get_rand_card()
        await message.channel.send(file=discord.File('card.png'))
    elif message.content[0:3].lower() == 'x.t':
        cards = glob.glob('cards/*')
        if len(nums) == 0:
            nums = requests.get("https://www.random.org/integers/", {'num':10, 'min':0, 'max':(len(cards)-1), 'format':'plain', 'rnd':'new', 'col':1, 'base':10}).content.split()
        await message.channel.send(file=discord.File(cards[int(nums[0])]))
        del nums[0]
    elif message.content[0:3] == 'qqb':
        bbq=['No.', 'Mote it be.', 'Never.', 'Yes.', 'I will it.', 'Absolutely not.', 'Yes, of course.', 'No', 'That will never happen.']
        await message.channel.send(bbq[randint(0,len(bbq)-1)])
    elif message.content[0:7] == 'x!quote':
        roles = list()
        for role in message.author.roles:
            roles.append(role.name)
        if "Quoter" in roles:
            if message.content[8:] == "":
                await message.channel.send('please provide an argument as a trigger ("x!quote bruh" and then type "moment")')
            else:
                await message.channel.send(f'next message will be read as quote for \"{message.content[8:]}\", type CANCEL to cancel this.')
                quote_queue[message.author.id] = message.content[8:]
    elif len(quote_queue) != 0:
        for user in quote_queue:
            if message.author.id == user:
                if message.content != 'CANCEL' and len(message.content) < 4:
                    await message.channel.send('only triggers over 4 characters are accepted!')
                elif message.content != 'CANCEL':
                    add_quote(quote_queue[message.author.id], message.content)
                    responses = retrieve_quotes()
                del quote_queue[message.author.id]
            break
    elif message.content.split()[0] == 'x!ltd' and message.author.id == 132620792818171905:
        if unltd:
            unltd = False
            await message.channel.send('*slow down*')
        else:
            unltd = True
            await message.channel.send('***BRAKES OFF*** <:based:620490020536451072>')
    elif message.content.split()[0] == 'x!ltds' and message.author.id == 132620792818171905:
        limit = int(message.content.split()[1])
        await message.channel.send(f'ratelimit set to ***{limit}*** seconds.')
    else:
        response = find_quote(responses, message.content)
        if response and ((message.author.id not in limited) or (message.author.id in limited and time.time()-limited[message.author.id] > limit) or unltd):
            limited[message.author.id] = time.time()
            await message.channel.send(response)
        elif response:
            await message.channel.send(f'shut, responses are ratelimited to ***{limit}*** seconds', delete_after=2)

client.run(token)
