import discord
import time
import json
import os
from discord.ext import commands

class raidmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis
        self.time_abbrev = {'s': 1, 'second': 1, 'seconds': 1, 'sec': 1, 'secs': 1,
                            'm': 60, 'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
                            'h': 3600, 'hr': 3600, 'hrs': 3600, 'hour': 3600, 'hours': 3600,
                            'd': 86400, 'day': 86400, 'days': 86400}
        self.joins = {}
        if os.path.isfile('persist/raidmode.json'):
            raidmode_buffer = json.load(open('persist/raidmode.json', 'r'))
            self.raidmode = {}
            for guild_id in raidmode_buffer:
                self.raidmode[int(guild_id)] = raidmode_buffer[guild_id]
                guild = bot.get_guild(int(guild_id))
                for join_id in raidmode_buffer[guild_id]["join_ids"]:
                    if guild: self.joins[join_id] = guild.get_member(raidmode_buffer[guild_id]["join_ids"][join_id])
        else:
            self.raidmode = {}
            json.dump(self.raidmode, open('persist/raidmode.json', 'w'))

    @commands.command()
    async def setup_raidmode(self, ctx, time_limit: int, arg, role: discord.Role):
        secs = 0
        if not arg in self.time_abbrev:
            await ctx.send('Please enter a valid time abbreviation! e.g. s, secs, m, min, minutes, hour, d, days, hr, etc.')
            return
        elif (self.time_abbrev[arg] * time_limit) > (self.time_abbrev['days'] * 3):
            await ctx.send('Sorry, bot only logs joins up to 3 days back.')
            return
        else:
            secs = self.time_abbrev[arg] * time_limit

        self.raidmode[ctx.guild.id] = {"role": role.id, "time_limit": secs, "raid": False, "time_title": (f'{time_limit} {arg}'), "join_ids": {}}
        json.dump(self.raidmode, open('persist/raidmode.json', 'w'))
        await ctx.send(f'role **{role.name}** has been set as the new autojoin role, joins will be logged up to {secs} seconds ({time_limit} {arg})')


    # turns on raid-mode, disable auto assigning verif role and strip it from joins in the last hour.
    @commands.command()
    async def raid(self, ctx, time_limit: int, arg):
        if not arg in self.time_abbrev:
            await ctx.send('Please enter a valid time abbreviation! e.g. s, secs, m, min, minutes, hour, d, days, hr, etc.')
            return
        else: time_limit *= self.time_abbrev[arg]

        if ctx.guild.id in self.raidmode and time_limit <= self.raidmode[ctx.guild.id]["time_limit"]:
            now = time.time()
            self.raidmode[ctx.guild.id]["raid"] = True
            joins = self.joins
            purged = 0
            for join in joins:
                if now-join < time_limit:
                    print('PURGING USER: ' + joins[join].name)
                    try:
                        add_role = ctx.guild.get_role(self.raidmode[ctx.guild.id]["role"])
                        await joins[join].add_roles(add_role)
                    except Exception: pass
                    finally: purged += 1
            json.dump(self.raidmode, open('persist/raidmode.json', 'w'))
            await ctx.send(f'raidmode enabled! **{purged}** users from the last hour have been sent to the verif channel.'+
                           'Verification is now required until raidmode is toggled back off.')
        elif ctx.guild.id in self.raidmode and time_limit > self.raidmode[ctx.guild.id]["time_limit"]:
            await ctx.send('sorry but at the moment joins on this server are only logged up to'+
                           f'**{self.raidmode[ctx.guild.id]["time_limit"]}** {time_limit} ago')
        else:
            ctx.send('Raidmode has not been setup for this server, please use +setup_raidmode')


    @commands.command()
    async def raid_off(self, ctx):
        if self.raidmode[ctx.guild.id]["raid"]:
            self.raidmode[ctx.guild.id]["raid"] = False
            json.dump(self.raidmode, open('persist/raidmode.json', 'w'))
            await ctx.send('raidmode disabled!')
        elif ctx.guild.id not in self.raidmode or not self.raidmode[ctx.guild.id]["raid"]:
            await ctx.send('raidmode is not enabled!')

    @commands.command()
    async def verif(self, ctx, member: discord.Member):
        roles = []
        for role in member.roles:
            roles.append(role.id)
        if not self.raidmode[member.guild.id]["role"] in roles:
            await ctx.send('user is already verified!')
            return
        else:
            joins_scope = self.raidmode[member.guild.id]["join_ids"]
            role = member.guild.get_role(self.raidmode[member.guild.id]["role"])
            await member.remove_roles(role)
            join_times = []
            for join_time in joins_scope:
                if member.id == joins_scope[join_time]:
                    join_times.append(joins_scope[join_time])
            for join_time in join_times:
                del self.raidmode[member.guild.id]["join_ids"][join_time]
            json.dump(self.raidmode, open('persist/raidmode.json', 'w'))
            ctx.send('verified!')

    # monitors joins to strip verif roles of recent joins if a raid occurs
    @commands.Cog.listener('on_member_join')
    async def join_logger(self, member):
        if member.guild.id in self.raidmode and self.raidmode[member.guild.id]:
            guildscope = self.raidmode[member.guild.id]
            now = time.time()
            while now in self.joins: now += 0.0001
            self.joins[now] = member
            guildscope["join_ids"][now] = member.id

            del_join = []
            for join in self.joins:
                if now-join > guildscope["time_limit"]: del_join.append(join)
            for join in del_join:
                del self.joins[join]
                del self.raidmode[member.guild.id]["join_ids"][join]
            json.dump(self.raidmode, open('persist/raidmode.json', 'w'))

            if guildscope["raid"]:
                role = member.guild.get_role(self.raidmode[member.guild.id]["role"])
                await member.add_roles(role)
                dm = await member.create_dm()
                await dm.send(f'Sorry! Right now we think a raid might be going on in **{member.guild.name}** so you will have to be verified.')

def setup(client):
    client.add_cog(raidmode(client))
