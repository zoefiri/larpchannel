import discord
import time
import json
import os
from discord.ext import commands

class COG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis

    # sends random tarot card
    @commands.command()
    async def CMD(self, ctx):
        pass

    # bbq
    @commands.Cog.listener('on_message')
    async def LISTEN(self, message):
        pass

def setup(client):
    client.add_cog(COG(client))
