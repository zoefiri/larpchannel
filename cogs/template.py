import discord
from discord.ext import commands

class MyCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def foo(self, ctx):

def setup(client):
    client.add_cog(MC(client))
