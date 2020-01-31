import discord
import requests
import time
import glob
import json
import os
from discord.ext import commands

class rng(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis

    # sends random tarot card
    @commands.command()
    async def tarot(self, ctx):
        redis = self.redis
        cards = glob.glob('cards/*')
        rand = redis.lpop('rands')
        if not rand:
            print('retrieving rand nums...')
            params = {'num':30, 'min':0, 'max':(len(cards)-1), 'format':'plain', 'rnd':'new', 'col':1, 'base':10}
            redis.lpush('rands', *(requests.get("https://www.random.org/integers/", params).content.split()))
            rand = redis.lpop('rands')
        await ctx.send(file=discord.File(cards[int(rand)]))
        print(rand, int(rand))

    # bbq
    @bot.listen('on_message')
    async def bbq(self, ctx):
        if context.message.content[0:2].lower() == 'bbq':
            bbq=['No.', 'Mote it be.', 'Never.', 'Yes.', 'I will it.', 'Absolutely not.', 'Yes, of course.', 'No', 'That will never happen.']
            await message.channel.send(bbq[randint(0,len(bbq)-1)])

def setup(client):
    client.add_cog(rng(client))
