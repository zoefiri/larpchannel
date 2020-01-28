import discord
from discord.ext import commands

class rng(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def tarot(self):
        pass

def setup(client):
    client.add_cog(rng(client))
