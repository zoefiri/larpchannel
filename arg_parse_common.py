# return dict with 'member' and 'role' keys, vals are False if error encountered, otherwise list with val and index found at
def user_role(args, ctx):
    parsed = {'member': False, 'role': False}
    for i in range(0,len(args)):
        if args[i][0:2] == '<@':
            parsed['member'] = ctx.guild.get_member(int(args[i].strip('<>@!')))
            role_candidate = ' '.join(args[0:i]).lower()
            break
    for role in ctx.guild.roles:
        if role.name.lower() == role_candidate: parsed['role'] = role
    return parsed

# return dict with 'member' as key, vals are False if error encountered.
def user(args, ctx):
    parsed = {'member': False}
    for i in range(0,len(args)):
        if args[i][0:2] == '<@':
            member = ctx.guild.get_member(int(args[i].strip('<>@!')))
            break
    return parsed

