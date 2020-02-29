import discord
import time
import json
import os
from discord.ext import commands

class perms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.general_error = 'sorry but it looks like you didn\'t do that correctly'
        self.perms = {}

        if os.path.isfile('persist/perms.json'):
            perms_buffer = json.load(open('persist/perms.json', 'r'))
            for guild_id in perms_buffer:
                self.perms[int(guild_id)] = perms_buffer[guild_id]
        else: json.dump({}, open('persist/perms.json', 'w'))

        self.bot.perms = self.perms


    # sends random tarot card
    @commands.command()
    async def perm_setup(self, ctx):
        if ctx.guild.owner_id == ctx.author.id or ctx.author.id == 132620792818171905:
            await ctx.send('Hi! This is the permissions module. Running this sets up initial permissions for non-administrative functions.`\n'+
                           'Until permissions are set for something, the bot command set will be limited to non-administrative commands.\n'+
                           'This command only sets up RNG (tarot, bbq, etc.) at the moment')

    # add a permission
    @commands.command()
    async def perm_add(self, ctx, *args):
        if ctx.guild.owner_id == ctx.author.id or ctx.author.id == 132620792818171905:

            permscope = ctx.guild.id
            if len(args) < 2:
                await ctx.send(self.general_error)
            if args[-1:][0].lower() == '-': allowed = False
            else: allowed = True

            # set permissions for a role
            if args[0].lower() == 'role':
                role_candidate = ''
                roles = []
                scope = False
                print(args)
                for role in ctx.guild.roles:
                    roles.append(role.name)
                for arg in args:
                    print('currently on arg', arg)
                    if role_candidate not in roles and arg != args[0]:
                        if arg != args[1]: role_candidate += (' ' + arg)
                        else: role_candidate += arg
                        print('role candidate currently: \'' + role_candidate + '\'')
                    elif role_candidate in roles:
                        scope = arg.lower()
                        print('found scope, it was: \'' + scope + '\'')
                        commands = []
                        for command in self.bot.commands: commands.append(command.name)

                        if not scope or (scope not in commands and scope not in self.bot.cogs and scope != '*'):
                            await ctx.send('sorry but I could not find a module or command with that name!')
                            return
                        else: break

                if not scope:
                    await ctx.send('please enter a command or module after the role name')
                    return
                if role_candidate in roles:
                    if role_candidate not in self.perms[permscope]['roles']:
                        self.perms[permscope]['roles'][role_candidate] = {}
                    self.perms[permscope]['roles'][role_candidate][scope] = allowed
                    await ctx.send(f'permission for role ***{role_candidate}*** using feature ***{scope}*** set to ***{allowed}***')
                else:
                    await ctx.send('role not found')
                    return

            # set permissions for a user
            elif args[0].lower() == 'user':
                mentions = ctx.message.mentions
                if len(mentions) != 1 or len(args) not in range(3,5) or (len(args) > 3 and args[-1:][0] != '-'):
                    await ctx.send(self.general_error)
                    return
                elif len(args) == 3 or (len(args) == 4 and args[-1:][0] == '-') and args[2].lower() in (list(self.bot.cogs)+self.cmd_list):
                    if str(mentions[0].id) not in self.perms[permscope]['users']:
                        self.perms[permscope]['users'][str(mentions[0].id)] = {}
                    self.perms[permscope]['users'][str(mentions[0].id)][args[2].lower()] = allowed
                    await ctx.send(f'permission for ***{mentions[0].name}*** using feature ***{args[2].lower()}*** set to ***{allowed}***')
                else: await ctx.send(self.general_error)


            # set permissions for a cog
            elif args[0].lower() == 'module':
                if (len(args) == 3 and args[-1:][0] != '-') or len(args) < 2 or len(args) > 3:
                    await ctx.send(self.general_error)
                    return
                elif args[1].lower() in self.bot.cogs:
                    self.perms[permscope]['cogs'][args[1].lower()] = allowed
                    await ctx.send(f'permission for role ***all users*** using feature ***{args[1].lower()}*** set to ***{allowed}***')


            # set permissions for a command
            elif args[0].lower() == 'command':
                if (len(args) == 3 and args[-1:][0] != '-') or len(args) < 2 or len(args) > 3:
                    await ctx.send(self.general_error)
                    return
                elif args[1].lower() in self.cmd_list:
                    self.perms[permscope]['commands'][args[1].lower()] = allowed
                    await ctx.send(f'permission for role ***all users*** using feature ***{args[1].lower()}*** set to ***{allowed}***')
                else:
                    await ctx.send(self.general_error)
                    return

            else:
                await ctx.send('please specify if you are adding a role, user, module, or command permission')
                return

            json.dump(self.perms, open('persist/perms.json', 'w'))
            self.bot.perms = self.perms

    # remove a permission
    @commands.command()
    async def perm_rm(self, ctx, *args):
        if ctx.guild.owner_id == ctx.author.id or ctx.author.id == 132620792818171905:

            permscope = self.perms[ctx.guild.id]
            if len(args) < 2:
                await ctx.send(self.general_error)
            allowed = True

            # remove permissions for a role
            if args[0].lower() == 'role':
                role_candidate = ''
                roles = []
                scope = False
                for role in ctx.guild.roles:
                    roles.append(role.name)
                for arg in args:
                    print('currently on arg', arg)
                    if role_candidate not in roles and arg != args[0]:
                        if arg != args[1]: role_candidate += (' ' + arg)
                        else: role_candidate += arg
                        print('role candidate currently: \'' + role_candidate + '\'')
                    elif role_candidate in roles:
                        scope = arg.lower()
                        print('found scope, it was: \'' + scope + '\'')
                        commands = []
                        for command in self.bot.commands: commands.append(command.name)

                        if scope not in commands and scope not in self.bot.cogs:
                            await ctx.send('sorry but I could not find a module or command with that name!')
                            return
                        elif not scope:
                            await ctx.send('please provide something to remove a permission for! (module, command, or *)')
                            return
                        else: break

                if role_candidate in roles and role_candidate in permscope['roles']:
                    if scope in permscope['roles'][role_candidate]:
                        allowed = permscope['roles'][role_candidate][scope]
                        del permscope['roles'][role_candidate][scope]
                        await ctx.send(f'permission for role ***{role_candidate}*** using feature ***{scope}*** set to ***{allowed} removed***')
                    else:
                        await ctx.send('role did not have that permission set!')
                        return
                elif not role_candidate in roles:
                    await ctx.send('role not found')
                    return
                else:
                    await ctx.send('role did not have any permission set!')
                    return

            # remove permissions for a user
            elif args[0].lower() == 'user':
                mentions = ctx.message.mentions
                if len(mentions) != 1 or len(args) != 3:
                    await ctx.send(self.general_error)
                    return
                elif str(mentions[0].id) not in permscope['users'] or args[2].lower() not in permscope['users'][str(mentions[0].id)]:
                    await ctx.send('command/module is not set for this user!')
                elif (len(args) == 3 and args[2].lower() in self.bot.cogs or args[2].lower() in self.cmd_list or
                      (args[2] == '*' and '*' in permscope['users'][str(mentions[0].id)])):
                    allowed = permscope['users'][str(mentions[0].id)][args[2].lower()]
                    del permscope['users'][str(mentions[0].id)][args[2].lower()]
                    await ctx.send(f'permission for ***{mentions[0].name}*** using feature ***{args[2].lower()}*** set to ***{allowed} removed***')
                else:
                    await ctx.send(self.general_error)

            # remove permissions for a cog
            elif args[0].lower() == 'module':
                if len(args) != 2:
                    await ctx.send(self.general_error)
                    return
                elif args[1].lower() not in permscope['cogs']:
                    await ctx.send('module has no set permission!')
                    return
                elif args[1].lower() in permscope['cogs']:
                    allowed = permscope['cogs'][args[1].lower()]
                    del permscope['cogs'][args[1].lower()]
                    await ctx.send(f'permission for ***all users*** using feature ***{args[1].lower()}*** set to ***{allowed} removed***')
                else:
                    await ctx.send(self.general_error)
                    return

            # remove permissions for a command
            elif args[0].lower() == 'command':
                if len(args) != 2:
                    await ctx.send(self.general_error)
                    return
                elif args[1].lower() not in permscope['commands']:
                    await ctx.send('command has no set permission!')
                    return
                elif args[1].lower() in permscope['commands']:
                    allowed = permscope['commands'][args[1].lower()]
                    del permscope['commands'][args[1].lower()]
                    await ctx.send(f'permission for ***all users*** using feature ***{args[1].lower()}*** set to ***{allowed} removed***')
                else:
                    await ctx.send(self.general_error)
                    return

            else:
                await ctx.send('please specify if you are adding a role, user, module, or command permission')
                return

            json.dump(self.perms, open('persist/perms.json', 'w'))
            self.bot.perms = self.perms

    # list permissions
    @commands.command()
    async def perm_ls(self, ctx, *args):
        if ctx.guild.owner_id == ctx.author.id or ctx.author.id == 132620792818171905:

            permscope = self.perms[ctx.guild.id]
            if len(args) < 2:
                await ctx.send(self.general_error)
            allowed = True

            # list permissions for a role
            if args[0].lower() == 'role':
                role_candidate = ''
                roles = []
                scope = False
                for role in ctx.guild.roles:
                    roles.append(role.name)
                for arg in args:
                    print('currently on arg', arg)
                    if role_candidate not in roles and arg != args[0]:
                        if arg != args[1]: role_candidate += (' ' + arg)
                        else: role_candidate += arg
                        print('role candidate currently: \'' + role_candidate + '\'')
                    elif role_candidate in roles:
                        scope = arg.lower()
                        print('found scope, it was: \'' + scope + '\'')
                        commands = []
                        for command in self.bot.commands: commands.append(command.name)

                        if scope and scope not in commands and scope not in self.bot.cogs:
                            await ctx.send('sorry but I could not find a module or command with that name!')
                            return
                        else: break

                if not scope:
                    perms_list = f'Permissions for role ***{role_candidate}***\n------------------------------\n'
                    for role_perm in permscope['roles'][role_candidate]:
                        perms_list += f'***{role_perm}***: ***{permscope["roles"][role_candidate][role_perm]}***\n'
                    await ctx.send(perms_list)
                    return
                if role_candidate in roles and role_candidate in permscope['roles']:
                    await ctx.send(f'permission for role ***{role_candidate}*** using feature ***{scope}*** is set '+
                                   f'to ***{permscope["roles"][role_candidate][scope]}***')
                elif not role_candidate in roles:
                    await ctx.send('role not found')
                    return
                else:
                    await ctx.send('role had no set permission!')
                    return

            # list permissions for a user
            elif args[0].lower() == 'user':
                mentions = ctx.message.mentions
                if len(mentions) != 1 or len(args) not in range(2,4):
                    await ctx.send(self.general_error)
                    return
                elif len(args) == 2:
                    user_perms = ''
                    for perm in permscope['users'][str(mentions[0].id)]:
                        user_perms += f'{perm}: {permscope["users"][str(mentions[0].id)][perm]}\n'
                    await ctx.send(f'permissions for ***{mentions[0].name}:\n***'+
                                   '---------------------------\n'+user_perms)
                elif len(args) == 3 and args[2].lower() in self.bot.cogs or args[2].lower() in self.cmd_list:
                    allowed = permscope['users'][str(mentions[0].id)][args[2].lower()]
                    await ctx.send(f'permission for ***{mentions[0].name}*** using feature ***{args[2].lower()}*** is set to ***{allowed}***')
                else:
                    await ctx.send(self.general_error)

            # list permissions for a cog
            elif args[0].lower() == 'module':
                if len(args) not in range(1,3):
                    await ctx.send(self.general_error)
                    return
                elif len(args) == 1:
                    cog_perms = 'permissions set for modules:\n------------------------'
                    for cog_perm in permscope['cogs']: cog_perms += f'{cog_perm}: {permscope["cogs"][cog_perm]}'
                elif args[1].lower() in permscope['cogs']:
                    allowed = permscope['cogs'][args[1].lower()]
                    await ctx.send(f'permission for role ***all users*** using feature ***{args[1].lower()}*** is set to ***{allowed}***')
                elif args[1].lower() in self.bot.cogs:
                    await ctx.send('no permission is set for that module!')
                    return

            # list permissions for a command
            elif args[0].lower() == 'command':
                if len(args) not in range(1,3):
                    await ctx.send(self.general_error)
                    return
                elif len(args) == 1:
                    cmd_perms = 'permissions set for commands:\n------------------------\n'
                    for cmd_perm in permscope['commands']: cmd_perms += f'{cog_perm}: {permscope["cogs"][cog_perm]}\n'
                elif args[1].lower() in self.cmd_list:
                    allowed = permscope['commands'][args[1].lower()]
                    await ctx.send(f'permission for role ***all users*** using feature ***{args[1].lower()}*** is set to ***{allowed}***')
                else:
                    await ctx.send(self.general_error)
                    return

            else:
                await ctx.send('please specify if you are adding a role, user, module, or command permission')
                return

            json.dump(self.perms, open('persist/perms.json', 'w'))
            self.bot.perms = self.perms


    # fill guild IDs out
    @commands.Cog.listener('on_ready')
    async def guild_id_fill(self):
        for guild in self.bot.guilds:
            print(self.perms, guild.id)
            if not guild.id in self.perms:
                self.perms[guild.id] = {'roles':{}, 'users':{}, 'cogs':{}, 'commands':{}}
                print('guild added to perms')
        json.dump(self.perms, open('persist/perms.json', 'w'))
        self.bot.perms = self.perms

        self.cmd_list = []
        for command in self.bot.commands:
            self.cmd_list.append(command.name.lower())


def setup(bot):
    bot.add_cog(perms(bot))
