def get_role(ctx, bot, args):
    roles = []
    for role in ctx.guild.roles:
        roles.append(role.name.lower())

    role_candidate = ""
    for arg, i in zip(args, range(0, len(args))):
        role_candidate += arg.lower()
        if role_candidate in roles: return {'role':role_candidate, 'len':i+1}
    return False

def get_cmd(ctx, bot, args):
    cmd_list = []
    for command in bot.commands:
        cmd_list.append(command.name.lower())
    if args[0].lower() in cmd_list: return args[0]
    else: return False

def get_cog(ctx, bot, args):
    if args[0].lower() in bot.cogs: return args[0]
    else: return False

def get_user(ctx, bot, args):
    if args[0][0:3] == '<@!' and args[0][-1:] == '>':
        return ctx.guild.get_member(int(args[3:-1]))

# required example = ['command', 'role', 'user', 'cog', 'int', 'another arbitrary string check(prefix % for optional)', [arbitrary_str OR  cog OR....], 
def parse(ctx, bot, required, args, extraneous=False):
    args = list(ctx.args)
    parsed = {'cogs':[], 'cmds':[], 'nums':[], 'roles':[], 'users':[], 'strcheck':[], 'orcheck':[], 'error':False}

    required_arg_count = 0
    for required_arg in required:
        if type(required_arg) == str and required_arg[0] == '%': pass
        else: required_arg_count += 1
    if len(args) < required_arg_count:
        parsed['error'] = 'not enough arguments were provided!'
        return parsed
    elif len(args) > required_arg_count and not extraneous:
        parsed['error'] = 'too many arguments were provided!'
        return parsed

    for required_arg in required:
        if required_arg == 'command':
            cmd_ret = get_cmd(ctx, bot, args)
            if cmd_ret:
                parsed['cmds'].append(cmd_ret)
                del args[0]
            else:
                parsed['error'] = 'command was not found.'
                return parsed

        elif required_arg == 'cog':
            cog_ret = get_cog(ctx, bot, args)
            if cog_ret:
                parsed['cogs'].append(cog_ret)
                del args[0]
            else:
                parsed['error'] = 'module was not found.'
                return parsed

        elif required_arg == 'role':
            role_ret = get_role(ctx, bot, args)
            if role_ret:
                parsed['roles'].append(role_ret['role'])
                args = args[role_ret['len':]]
            else:
                parsed['error'] = 'module was not found.'
                return parsed

        elif required_arg == 'user':
            user_ret = get_user(ctx, bot, args)
            if user_ret:
                parsed['users'].append(user_ret)
                del args[0]
            else:
                parsed['error'] = 'user was not found.'
                return parsed

        elif required_arg == 'int':
            if args[0].isdigit():
                parsed['nums'].appent(int(args[0]))
                del args[0]
            else:
                parsed['error'] = 'number was not provided, or argument was not a number!'
                return parsed

        elif type(required_arg) == str:
            optional = True if args[0][0] == '%' else False
            if optional: required_arg = required_arg[1:]

            if args[0].lower() == required_arg:
                parsed['strcheck'].append(args[0])
                del args[0]
            elif not optional:
                parsed['error'] = 'argument error, please refer to the command\'s help.'
                return parsed

        elif type(required_arg) == list:
            matched = False
            for or_arg in required_arg:
                if or_arg == 'command':
                    cmd_ret = get_cmd(ctx, bot, args)
                    if cmd_ret:
                        parsed['orcheck'].append(cmd_ret)
                        del args[0]
                        matched = True
                        break

                elif or_arg == 'cog':
                    cog_ret = get_cog(ctx, bot, args)
                    if cog_ret:
                        parsed['orcheck'].append(cog_ret)
                        del args[0]
                        matched = True
                        break

                elif or_arg == 'role':
                    role_ret = get_role(ctx, bot, args)
                    if role_ret:
                        parsed['orcheck'].append(role_ret['role'])
                        args = args[role_ret['len']:]
                        matched = True
                        break

                elif or_arg == 'user':
                    user_ret = get_user(ctx, bot, args)
                    if user_ret:
                        parsed['orcheck'].append(user_ret)
                        del args[0]
                        matched = True
                        break

                elif or_arg == 'int':
                    if args[0].isdigit():
                        parsed['orcheck'].appent(int(args[0]))
                        del args[0]
                        matched = True
                        break

                elif type(or_arg) == str:
                    if args[0].lower() == or_arg:
                        parsed['orcheck'].append(args[0])
                        del args[0]
                        matched = True
                        break

            if not matched: parsed['error'] = 'argument error, please refer to command help.'
            return parsed
