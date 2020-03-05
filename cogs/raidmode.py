import discord
import time
import json
import os
from discord.ext import commands

class raidmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis
        # 0 - raidmode OFF, 1 - enable verif channel and strip verified role off last x joins, 2 - enable #general slowmoding, 3 - enable ALL
        self.raidmode = False
        self.verif_role_name = 'xyzygian'
        self.verif_role = get_role()
        self.joins = {}

    # turns on raid-mode, disable auto assigning verif role and strip it from joins in the last hour.
    @commands.command()
    async def raid(self, ctx):
        now = time.time()
        if self.raidmode:
            self.raidmode = False
            await ctx.send('raidmode disabled!')

        elif not self.raidmode:
            self.raidmode = True
            removed = []
            for join in self.joins:
                roles = []
                for role in self.joins[join].roles: roles.append(role.name.lower())
                if now-join < 3600 and self.verif_role_name in roles:
                    try: await self.joins[join].remove_roles(self.verif_role)
                    except Exception: pass
                    finally: removed.append(join)

            await ctx.send(f'raidmode enabled! **{len(removed)}** users from the last hour have been sent to the verif channel.'+
                           'Verification is now required until raidmode is toggled back off.')

            for join in removed: del self.joins[join]



    # monitors joins to strip verif roles of recent joins if a raid occurs
    @commands.Cog.listener('on_member_join')
    async def join_logger(self, member):
        now = time.time()
        while now in self.joins: now += 0.0001
        self.joins[now] = member

        for join in self.joins:
            if now-join > 4000:
                del self.joins[join]

def setup(client):
    client.add_cog(raidmode(client))
