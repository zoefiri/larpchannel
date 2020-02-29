import discord
import threading
import time
import json
import sys
import os
import arg_parse_common as parse
from recordtype import recordtype
from discord.ext import commands
from discord.ext.tasks import loop

class timed_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_schedule_lock = threading.Lock()
        self.limited = {}
        bot.timed_roles = self

        self.no_role_err = 'sorry but I couldn\'t find that role'
        self.no_user_err = 'sorry but I couldn\'t find that user'
        self.mention_err = 'sorry, you provided more than 1 mention or no mentions.'
        self.time_err = 'sorry but you either didn\'t give a time or provided it wrong, I take seconds, minutes, hours, and days.'
        self.no_arg_err = 'please provide a user tag (@user).'
        self.rate_err = 'sorry but it looks like you entered the time to limit the user for incorrectly'
        self.missing_args_err = 'sorry but it looks like you didn\'t provide all the needed arguments'

        if os.path.isfile('persist/role_schedule.json'):
            role_schedule_buffer = json.load(open('persist/role_schedule.json', 'r'))
            self.role_schedule = {}
            for key in role_schedule_buffer:
                self.role_schedule[float(key)] = role_schedule_buffer[key]
        else:
            self.role_schedule = {}
            json.dump({}, open('persist/role_schedule.json', 'w'))

        if os.path.isfile('persist/limited.json'):
            limited_buffer = json.load(open('persist/limited.json', 'r'))
            self.limited = {}
            limited_info = recordtype('limited_info', 'rate guild_id, last_sent violations last_violated')

            for key in limited_buffer:
                val = limited_buffer[key]
                self.limited[int(key)] = limited_info(val[0], val[1], val[2], val[3], val[4])
        else:
            self.limited = {}
            json.dump({}, open('persist/limited.json', 'w'))

    # timed role assign
    @commands.command()
    async def tr(self, ctx, *args):
        help_msg = ('\ntr - adds a timed role\n'+
                    'usage: `+tr <rolename> @user <time> <unit>`\n'+
                    'example: `+tr role @zoefiri 10 secs`')
        message = ctx.message
        now = time.time()
        member = False
        member_index = 0
        time_abbrev = {'s': 1, 'second': 1, 'seconds': 1, 'sec': 1, 'secs': 1,
                       'm': 60, 'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
                       'h': 3600, 'hr': 3600, 'hrs': 3600, 'hour': 3600, 'hours': 3600,
                       'd': 86400, 'day': 86400, 'days': 86400}
        # Check perms
        for role in ctx.author.roles:
            timed_role = False
            if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                if len(message.mentions) != 1:
                    await ctx.send(self.mention_err+help_msg)

                # acquire role and user
                for i in range(0,len(args)):
                    if args[i][0:2] == '<@':
                        role_candidate = ' '.join(args[0:i]).lower()
                        member_index = i
                        break
                for role in ctx.guild.roles:
                    if role.name.lower() == role_candidate: timed_role = role
                member = message.mentions[0]

                # check if user and role exist, and if time has been entered properly.
                if not timed_role:
                    await ctx.send(self.no_role_err+help_msg)
                    return
                if not member:
                    await ctx.send(self.no_user_err+help_msg)
                    return
                try:
                    role_duration = int(args[member_index+1]) * time_abbrev[args[member_index+2]]
                except (KeyError, ValueError, IndexError):
                    await message.channel.send(self.time_err+help_msg)
                    return

                # add role to the schedule
                await member.add_roles(timed_role)
                new_role_detail = {'member': member.id, 'role': timed_role.name, 'assigned': now,
                                   'duration': role_duration, 'guild': message.guild.id}
                self.role_schedule_lock.acquire()
                try:
                    while now+role_duration in self.role_schedule:
                        role_duration += .0001

                    self.role_schedule[now+role_duration] = new_role_detail
                    json.dump(self.role_schedule, open('persist/role_schedule.json', 'w'))
                finally:
                    self.role_schedule_lock.release()

                await message.channel.send(f'user **{member.name}** given role **{timed_role.name}** for '+
                                           f'**{args[member_index+1]+" "+args[member_index+2]}** (**{role_duration}** seconds)')
                return

    # timed roles list
    @commands.command()
    async def trls(self,ctx, arg):
        if len(ctx.message.mentions) != 1:
            await ctx.send(self.mention_err+help_msg)
        else:
            member = ctx.message.mentions[0]
            if member:
                msg_header = f'timed roles for user **{member.name}**:\n'
                msg = ''
                for role in self.role_schedule:
                    if role['member'] == member.id:
                        msg += (f'**{role["role"]}** assigned for **{role["duration"]}** seconds with '+
                                f'**{int(role["duration"]-(time.time()-role["assigned"]))}** remaining\n')
                if not msg:
                    await ctx.send(f'user **{member.name}** has no timed roles.')
                    return
                else:
                    await ctx.send(msg_header+msg)
            else:
                ctx.send(self.no_user_err)

    #manual timed role remover
    @commands.command()
    async def trm(self,ctx, *args):
        help_msg = ('\ntrm - removes a timed role\n'+
                    'usage: +tr <rolename> @user'+
                    'example: +trm role @zoefiri')
        message = ctx.message
        # Check perms
        for role in ctx.author.roles:
            timed_role = False
            if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                if len(message.mentions) != 1:
                    await ctx.send(self.mention_err+help_msg)

                # acquire role and user
                for i in range(0,len(args)):
                    if args[i][0:2] == '<@':
                        role_candidate = ' '.join(args[0:i]).lower()
                        member_index = i
                        break
                for role in ctx.guild.roles:
                    if role.name.lower() == role_candidate: timed_role = role
                member = message.mentions[0]

                # check if user and role exist, and if time has been entered properly.
                if not timed_role:
                    await ctx.send(self.no_role_err+help_msg)
                    return
                if not member:
                    await ctx.send(self.no_user_err+help_msg)
                    return

                print('role rming')
                # remove role from the schedule.
                deleting = False
                for role in self.role_schedule.values():
                    if role['member'] == member.id and role['role'] == timed_role.name:
                        for guild_role in ctx.guild.roles:
                            if guild_role.name.lower() == timed_role.name.lower():
                                await member.remove_roles(guild_role)
                                deleting = role['duration']+role['assigned']
                                await ctx.send(f'removed **{guild_role.name}** from user **{member.name}**')
                                break
                    else:
                        await ctx.send('member doesn\'t have this timed role!')

                if deleting:
                    self.role_schedule_lock.acquire()
                    try:
                        del self.role_schedule[deleting]
                        json.dump(self.role_schedule, open('persist/role_schedule.json', 'w'))
                    finally:
                        self.role_schedule_lock.release()

    # timed roles remover
    @loop(seconds=1.0)
    async def role_remover(bot):
        try:
            now = time.time()
            removing = False
            self = bot.timed_roles
            for role_expiry in self.role_schedule:
                role_expiring = self.role_schedule[role_expiry]
                print('EXPIRY', role_expiry)
                if role_expiry < now:
                    removal_role = False
                    removal_guild = False
                    for guild in bot.guilds:
                        if guild.id == role_expiring['guild']:
                            removal_guild = guild
                    for role in removal_guild.roles:
                        if role.name == role_expiring['role']: removal_role = role
                    member = removal_guild.get_member(role_expiring['member'])
                    if removal_role:
                        await member.remove_roles(removal_role)
                    removing = True
            if removing:
                delete = [key for key in self.role_schedule if key < now]
                self.role_schedule_lock.acquire()
                try:
                    for deletion in delete:
                        del self.role_schedule[deletion]
                    json.dump(self.role_schedule, open('persist/role_schedule.json', 'w'))
                finally:
                    self.role_schedule_lock.release()
        except Exception as e:
            print(e)
            print(sys.exc_info()[-1].tb_lineno)

    # role persist for timed roles
    @commands.Cog.listener('on_member_join')
    async def role_persist(self, member):
        for role in self.role_schedule:
            if member.id == self.role_schedule[role]['member'] and role > time.time():
                for guild_role in member.guild.roles:
                    if guild_role.name == self.role_schedule[role]['role']: await member.add_roles(guild_role)

    # ratelimit setter
    @commands.command()
    async def limit(self, ctx, *args):
        help_msg = ('\nlimit - ratelimits a user\n'+
                    '`usage: +limit @user <secs>`\n'+
                    '`example: +limit @zoefiri 30`')

        # check if required argument and mention count is met
        if len(ctx.message.mentions) != 1:
            await ctx.send(self.mention_err+help_msg)
        if len(args) < 2:
            await ctx.send(self.missing_args_err+help_msg)

        # acquire user
        member = ctx.message.mentions[0]

        # check if user exists and time entered correctly
        if not member:
            await ctx.send(self.no_user_err+help_msg)
            return
        try:
            rate = int(args[1])
        except (ValueError, IndexError):
            await ctx.send(self.rate_err+help_msg)
            return

        # setup user limit
        limited_info = recordtype('limited_info', 'rate guild_id, last_sent violations last_violated')
        self.limited[member.id] = limited_info(rate, ctx.guild.id, time.time()-rate, 0, 0)

        limited_json = json.load(open('persist/limited.json', 'r'))
        limited_json[member.id] = [rate, ctx.guild.id, time.time()-rate, 0, 0]
        json.dump(limited_json, open('persist/limited.json', 'w'))
        await ctx.send(f'user ratelimited to ***{rate}*** seconds')

    # ratelimit deleter
    @commands.command()
    async def unlimit(self, ctx, *args):
        help_msg = ('\nunlimit - removes user\'s ratelimit\n'+
                    '`usage: +unlimit @user`\n'+
                    '`example: +unlimit @zoefiri`')

        # check if required argument and mention count is met
        if len(ctx.message.mentions) != 1:
            await ctx.send(self.mention_err+help_msg)
        if len(args) < 1:
            await ctx.send(self.missing_args_err+help_msg)

        # acquire user
        member = ctx.message.mentions[0]

        # check if user exists and then remove limit
        if not member:
            await ctx.send(self.no_user_err+help_msg)
            return
        if member.id in self.limited and self.limited[member.id].guild_id == ctx.guild.id:
            rate = self.limited[member.id].rate
            limited_json = json.load(open('persist/limited.json', 'r'))
            del self.limited[member.id]
            del limited_json[str(member.id)]

            json.dump(limited_json, open('persist/limited.json', 'w'))
            await ctx.send(f'user ratelimit of ***{rate}*** seconds lifted')
        else:
            await ctx.send('user isn\'t ratelimited!')

    # ratelimit query
    @commands.command()
    async def limitq(self, ctx, *args):
        help_msg = ('\nunlimit - removes user\'s ratelimit\n'+
                    '`usage: +unlimit @user`\n'+
                    '`example: +unlimit @zoefiri`')

        # check if required argument and mention count is met
        if len(ctx.message.mentions) != 1:
            await ctx.send(self.mention_err+help_msg)
        if len(args) < 1:
            await ctx.send(self.missing_args_err+help_msg)

        # acquire user
        member = ctx.message.mentions[0]

        # check if user exists and then send limit
        if not member:
            await ctx.send(self.no_user_err+help_msg)
            return
        if member.id in self.limited and self.limited[member.id].guild_id == ctx.guild.id:
            rate = self.limited[member.id].rate
            await ctx.send(f'user is ratelimited to ***{rate}*** seconds')
        else:
            await ctx.send('user isn\'t ratelimited!')

    # ratelimit enforcer
    @commands.Cog.listener('on_message')
    async def ratelimit_enforcer(self, message):
        if message.author.id in self.limited:
            ltd_user = self.limited[message.author.id]
            print('last time + rate: ' + str(time.time()-ltd_user.last_sent) + ' ' + str(ltd_user.rate))
            if message.guild.id == ltd_user.guild_id and time.time()-ltd_user.last_sent < ltd_user.rate:
                now = time.time()
                await message.delete()

                if (ltd_user.violations >= 10 or ltd_user.violations > 3 and now-ltd_user.last_violated <= 2):
                    await message.author.add_roles(message.guild.get_role(666168181798469672))
                    new_role_detail = {'member': message.author.id, 'role': 'Muted', 'assigned': now,
                                       'duration': 30, 'guild': message.guild.id}
                    self.role_schedule_lock.acquire()
                    try:
                        self.role_schedule[now+30] = new_role_detail
                        json.dump(self.role_schedule, open('persist/role_schedule.json', 'w'))
                    finally:
                        self.role_schedule_lock.release()

                ltd_user.violations += 1
                ltd_user.last_violated = now
            else:
                ltd_user.last_sent = time.time()

def setup(bot):
    timed_roles.role_remover.start(bot)
    bot.add_cog(timed_roles(bot))
