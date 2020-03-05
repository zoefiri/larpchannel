import discord
import time
import json
import os
from discord.ext import commands
from parse import parse

class purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # purge messages
    @commands.command()
    async def purge(self, ctx):
        parse(ctx, bot, args, [[]])

def setup(client):
    client.add_cog(purge(client))
