import discord
import itertools
import requests
import time
import glob
import json
import os
from random import seed, randint
from driv import get_rand_card

seed(time.time())

class cmds:
    # sends random yugioh card
    class yugioh:
        help_text = ("spits out a random yugioh card\n"+
                     "\t**usage**: `yugioh!`")
        command_text = "yugioh!"
        async def action(message, cmd_globals):
            get_rand_card()
            await message.channel.send(file=discord.File('card.png'))

    # sends random tarot card
    class tarot:
        help_text = ("spits out a tarot card\n"+
                     "\t**usage**: `x.t`")
        command_text = "x.t"
        async def action(message, cmd_globals):
            cards = glob.glob('cards/*')
            if len(cmd_globals['nums']) == 0:
                print('retrieving rand nums...')
                params = {'num':5, 'min':0, 'max':(len(cards)-1), 'format':'plain', 'rnd':'new', 'col':1, 'base':10}
                cmd_globals['nums'] = requests.get("https://www.random.org/integers/", params).content.split()
            await message.channel.send(file=discord.File(cards[int(cmd_globals['nums'][0])]))
            del cmd_globals['nums'][0]

    # sends random tarot card
    class tarot_batch:
        help_text = ("returns a list of tarot draws\n"+
                     "\t**usage**: `x.tb <num>`")
        command_text = "x.tb"
        async def action(message, cmd_globals):
            try:
                draw_count = int(message.content.split()[1])
            except (ValueError, IndexError):
                await message.channel.send('sorry, please provide a number of cards to draw.')
                return
            if draw_count > 25:
                await message.channel.send('sorry, only 25 draws at a time please!')
                return
            if draw_count < 0:
                await message.channel.send('sorry, only draws of numbers over 0!')
                return

            print('retrieving rand nums...')
            params = {'num':draw_count, 'min':0, 'max':78, 'format':'plain', 'rnd':'new', 'col':1, 'base':10}
            nums = requests.get("https://www.random.org/integers/", params).content.split()
            msg = ''
            for num in nums:
                msg += (str(int(num)) + ' ')
            await message.channel.send(f'```[{msg[:-1]}]```')

    # bbq
    class bbq:
        help_text = ("spits out a bbq response\n"+
                     "\t**usage**: `qqb`")
        command_text = "qqb"
        async def action(message, cmd_globals):
            bbq=['No.', 'Mote it be.', 'Never.', 'Yes.', 'I will it.', 'Absolutely not.', 'Yes, of course.', 'No', 'That will never happen.']
            await message.channel.send(bbq[randint(0,len(bbq)-1)])

    # quote adder
    class quote_add:
        help_text = ("adds a trigger-quote pair\n"+
                     "\t**usage**: `+quote <trigger>` (then respond with desired quote text)")
        command_text = "+quote"
        async def action(message, cmd_globals):
            roles = list()
            for role in message.author.roles:
                roles.append(role.name)
            if "Quoter" in roles:
                if message.content[7:] == "":
                    await message.channel.send('please provide an argument as a trigger ("+quote bruh" and then type "moment")')
                else:
                    await message.channel.send(f'next message will be read as quote for \"{message.content[7:]}\", type CANCEL to cancel this.')
                    cmd_globals['quote_queue'][message.author.id] = message.content[7:]

    # quote adder (response receptor)
    class quote_add_receptor:
        custom_logic = 1
        async def action(message, cmd_globals):
            if len(cmd_globals['quote_queue']) != 0:
                for user in cmd_globals['quote_queue']:
                    if message.author.id == user:
                        if message.content != 'CANCEL' and len(message.content) < 4:
                            await message.channel.send('only triggers over 4 characters are accepted!')
                        elif message.content != 'CANCEL':
                            cmd_globals['responses'][cmd_globals['quote_queue'][message.author.id]] = message.content
                            json.dump(cmd_globals['responses'], open('responses.json', 'w'))
                        del cmd_globals['quote_queue'][message.author.id]
                    break

    # quote deleter
    class quote_delete:
        command_text = "+del_quote"
        help_text = ("removes a trigger-quote pair\n"+
                     "\t**usage**: `+del_quote <trigger>`")
        async def action(message, cmd_globals):
            cmd_args = ' '.join(message.content.split()[1:])
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                if cmd_args in list(cmd_globals['responses'].keys()):
                    del cmd_globals['responses'][cmd_args]
                    json.dump(cmd_globals['responses'], open('responses.json', 'w'))
                    await message.channel.send('quote was deleted succesfully!')
                else:
                    await message.channel.send('sorry, looks like that quote doesn\'t exist.')

    # quote trigger ratelimit toggler
    class quote_rate_toggle:
        command_text = "+ltd"
        help_text = ("toggles quote triggering rate limiting\n"+
                     "\t**usage**: `+ltd`")
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                if cmd_globals['unltd']:
                    cmd_globals['unltd'] = False
                    await message.channel.send('*slow down*')
                else:
                    cmd_globals['unltd'] = True
                    await message.channel.send('***BRAKES OFF*** <:based:620490020536451072>')

    # ratelimit setter
    class quote_rate_setter:
        help_text = ("sets quote triggering rate limit\n"+
                     "\t**usage**: `+ltds <ratelimit (seconds)>`")
        command_text = "+ltds"
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                cmd_globals['limit'] = int(message.content.split()[1])
                cmd_globals['limited'] = {}
                await message.channel.send(f'ratelimit set to ***{cmd_globals["limit"]}*** seconds.')

    # quote trigger replier 
    class quote_replier:
        custom_logic = 1
        async def action(message, cmd_globals):
            try:
                response = cmd_globals['responses'][message.content.lower()]
            except KeyError:
                return
            if response and ((message.author.id not in cmd_globals['limited']) or (message.author.id in cmd_globals['limited'] and time.time()-cmd_globals['limited'][message.author.id] > cmd_globals['limit']) or cmd_globals['unltd']):
                cmd_globals['limited'][message.author.id] = time.time()
                await message.channel.send(response)
            elif response:
                await message.channel.send(f'shut, responses are ratelimited to ***{cmd_globals["limit"]}*** seconds', delete_after=1)

    # deletes messages from ratelimited person
    class ratelimit_enforce:
        custom_logic = 1
        async def action(message, cmd_globals):
            if message.author.id in cmd_globals['slowed']:
                limited_user = cmd_globals['slowed'][message.author.id]
                if (time.time()-limited_user['sent']) < limited_user['rate']:
                    await message.delete()
                    limited_user['violated'] += 1
                    limited_user['violated_time'] = time.time()
                    if limited_user['violated'] >= 10 or (limited_user['violated'] > 3 and time.time()-limited_user['violated_time'] <= 2):
                        await message.author.add_roles(message.guild.get_role(666168181798469672))
                        cmd_globals['role_timed'][str(message.author.id) + "muted"] = {'member': message.author.id, 'role': "muted",
                                                                                       'assigned': time.time(), 'duration': 30,
                                                                                       'guild': message.guild.id}
                        json.dump(cmd_globals['role_timed'], open('role_schedule.json', 'w'))
                        limited_user['violated'] = 0
                        print(cmd_globals['role_timed'])
                else:
                    limited_user['sent'] = time.time()

    # slowmode style "ratelimit" a user.
    class ratelimit_add:
        command_text = "+limit"
        help_text = ("put a ratelimit on a user\n"+
                     "\t**usage**: `+limit <@user> <ratelimit (secs)>`\n"+
                     "\t**example**: +limit @zoefiri 10")
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                cmd_args = message.content.split()
                try:
                    member = int(cmd_args[1].strip('<>@!'))
                except (KeyError, ValueError, IndexError):
                    await message.channel.send('sorry but it looks like you didn\'t provide a valid tag.\n**usage:** +limit <@user> <limit (secs)>')

                try:
                    rate = int(cmd_args[2])
                except (KeyError, ValueError, IndexError):
                    await message.channel.send('sorry but it looks like you didn\'t provide a valid time.\n**usage:** +limit <@user> <limit (secs)>')

                if rate > 60 or rate < 1:
                    await message.channel.send('sorry, invalid ratelimit. Only ratelimits 1-60 seconds.')
                    return
                cmd_globals['slowed'][member] = {'sent': time.time()-rate, 'rate': rate, 'violated': 0, 'violated_time': 0}
                json.dump(cmd_globals['slowed'], open("ratelimit.json", "w"))
                await message.channel.send(f'user ratelimited to {rate} seconds!')

    # remove a ratelimit from a user.
    class ratelimit_remove:
        command_text = "+unlimit"
        help_text = ("remove ratelimit off of a user\n"+
                     "\t**usage**: `+unlimit <@user>`\n"+
                     "\t**example**: +unlimit @zoefiri")
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                cmd_args = message.content.split()
                try:
                    member = int(cmd_args[1].strip('<>@!'))
                except (KeyError, ValueError, IndexError):
                    await message.channel.send('sorry but it looks like you didn\'t provide a valid tag.\n**usage:** +unlimit <@user>')

                if member in cmd_globals['slowed']:
                    del cmd_globals['slowed'][member]
                    json.dump(cmd_globals['slowed'], open("ratelimit.json", "w"))
                    await message.channel.send(f'user\'s ratelimit removed!')
                else:
                    await message.channel.send(f'user\'s not ratelimited!')

    # query user's ratelimit
    class ratelimit_query:
        command_text = "+limit?"
        help_text = ("show current ratelimit on a user\n"+
                     "\t**usage**: `+limit? <@user>`\n"+
                     "\t**example**: +limit? @zoefiri")
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                cmd_args = message.content.split()
                try:
                    member = int(cmd_args[1].strip('<>@!'))
                except (KeyError, ValueError, IndexError):
                    await message.channel.send('sorry but it looks like you didn\'t provide a valid tag.\n**usage:** +unlimit <@user>')

                if member in cmd_globals['slowed']:
                    await message.channel.send(f'user\'s ratelimit is {cmd_globals["slowed"][member]["rate"]}!')
                else:
                    await message.channel.send(f'user\'s not ratelimited!')

    # role timed
    class timed_role:
        command_text = "+t_role"
        help_text = ("add a role to a user for a limited duration of time\n"+
                     "\t**usage**: `+t_role <role> <@user> <duration> <time unit>`\n"+
                     "\t**example**: +t_role rose @zoefiri 1 hour")
        async def action(message, cmd_globals):
            for role in message.author.roles:
                if role.name == 'Mods' or role.name == 'Admins' or message.author.id == 132620792818171905:
                    permitted = True
                    break
                else:
                    permitted = False

            if permitted:
                timed_role = False
                role_candidate = []
                for i, arg in zip(range(0, len(message.content.split())), message.content.split()[1:]):
                    if arg[0:2] == '<@':
                        member = message.guild.get_member(int(arg.strip('<>@!')))
                        iterc = i+2
                        break
                    role_candidate.append(arg)
                print(role_candidate, "was the role")
                for role in message.guild.roles:
                    if role.name.lower() == (' '.join(role_candidate)).lower(): timed_role = role
                if not timed_role:
                    print(role.name.lower() + '-' + ' '.join(role_candidate).lower())
                    print('FUCKKKKYYY!')
                    await message.channel.send('sorry but I couldn\'t find that role')
                    return
                try:
                    if not member:
                        print(int(message.content.split()[2].strip('<>@!')))
                        print(member)
                        await message.channel.send('sorry but I couldn\'t find the specified user')
                        return
                except ValueError:
                    await message.channel.send('sorry but I couldn\'t find the specified user')
                    return

                time_abbrev = {'s': 1, 'second': 1, 'seconds': 1, 'sec': 1, 'secs': 1,
                               'm': 60, 'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
                               'h': 3600, 'hr': 3600, 'hrs': 3600, 'hour': 3600, 'hours': 3600,
                               'd': 86400, 'day': 86400, 'days': 86400}
                try:
                    role_duration = int(message.content.split()[iterc]) * time_abbrev[message.content.split()[iterc+1]]
                except (KeyError, ValueError, IndexError):
                    await message.channel.send('sorry but it looks like you didn\'t provide a time or typed the time wrong'+
                                               '(I only accept secs, mins, hours, and days.)')
                    return

                await member.add_roles(timed_role)
                cmd_globals['role_timed'][str(member.id) + timed_role.name] = {'member': member.id, 'role': timed_role.name, 'assigned': time.time(),
                                                                               'duration': role_duration, 'guild': message.guild.id}
                json.dump(cmd_globals['role_timed'], open('role_schedule.json', 'w'))
                space = ' '
                await message.channel.send(f'user **{member.name}** given role **{timed_role.name}** for '+
                                           f'**{space.join(message.content.split()[3:])}** (**{role_duration}** seconds)')

    # role unschedule
    class role_unschedule:
        help_text = ("remove a timed role from a user\n"+
                     "\t**usage**: `+role_unscehdule <role> <@user>`\n"+
                     "\t**example**: `+role_unschedule rose @zoefiri`")
        command_text = "+t_unrole"
        async def action(message, cmd_globals):
            print(cmd_globals['role_timed'])
            member_id = int(message.content.split()[2].strip('<>@!'))
            member = message.guild.get_member(member_id)
            for role in message.guild.roles:
                if role.name.lower() == message.content.split()[1].lower():
                    timed_role_name = role.name
                    role_user_str = str(member.id)+timed_role_name
                    timed_role = role
            if not timed_role:
                await message.channel.send('role was not found')
                return
            if not member:
                await message.channel.send('member was not found')
                return
            if not role_user_str in list(cmd_globals['role_timed'].keys()):
                await message.channel.send('member has no timed roles')
                return

            del cmd_globals['role_timed'][role_user_str]
            await member.remove_roles(timed_role)
            await message.channel.send(f'**{timed_role_name}** removed from **{member.name}**')

    # role list
    class role_list:
        help_text = ("list roles assigned to a user"+
                     "\t**usage**: `+role_ls <@user>`\n"+
                     "\t**example**: `+role_ls @zoefiri`")
        command_text = "+role_ls"
        async def action(message, cmd_globals):
            print(cmd_globals['role_timed'])
            member_id = int(message.content.split()[1].strip('<>@!'))
            member = message.guild.get_member(member_id)
            member_roles = []
            timed_list = cmd_globals['role_timed']
            for role in cmd_globals['role_timed']:
                if timed_list[role]['member'] == member_id:
                    member_roles.append(timed_list[role])
            if not member:
                await message.channel.send('member was not found')
                return
            if len(member_roles) == 0:
                await message.channel.send('member has no timed roles')
                return
            print(member_roles)

            msg = ""
            for role in member_roles:
                time_left = role['duration']-(time.time()-role['assigned'])
                msg += (f'**{role["role"]}**: {time_left:.0f} secs ({(time_left/60):.2f}'+
                        f'minutes ({(time_left/3600):.2f} hours ({(time_left/86400):.2f} days)))\n')
            await message.channel.send(msg)

    # help cmd
    class help:
        help_text = ("show help\n"+
                     "\t**usage**: `+help` OR `+help <command>`\n"+
                     "\t**example**: `+help OR +help +t_role`")
        command_text = "+help"

        async def action(message, cmd_globals):
            err_msg = ('sorry couldn\'t find that command or you asked for help on more than one thing\n'+
                       '**usage:** `+help` OR `+help <command>`')
            command_msg = message.content.split()
            msg_text = ""

            if len(command_msg) == 1:
                for command in list(cmd_globals['help_info'].keys()):
                    msg_text += f"**{command}**: " + cmd_globals['help_info'][command] + '\n\n'
                await message.channel.send(msg_text)

            elif len(command_msg) == 2:
                msg_text += f"**{command_msg[1]}**: "
                try:
                    msg_text += cmd_globals['help_info'][command_msg[1].lower()]
                except KeyError:
                    await message.channel.send(err_msg)
                    return
                await message.channel.send(msg_text)

            else:
                await message.channel.send(err_msg)



