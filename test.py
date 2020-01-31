import discord
from discord.ext import commands
from discord.ext.tasks import loop

token = 'NjY2Mjg5ODE1ODE3Mjg5NzM4.XjRKug.hLMDddmi9mDv4wzmmE55Em4hFaw'
bot = commands.Bot(command_prefix='+')

exts = ['cogs.rng']

for ext in exts:
    bot.load_extension(ext)

bot.run(token)
