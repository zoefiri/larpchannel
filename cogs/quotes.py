import time
from discord.ext import commands

class quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = bot.redis
        self.quote_queue = {}
        self.limited = {}
        self.limit = 60

    # quote adder
    @commands.command()
    async def quote(self, ctx):
        for role in ctx.message.author.roles:
            if role.name == "Quoter":
                if ctx.message.content[7:] == "":
                    await ctx.send('please provide an argument as a trigger ("+quote bruh" and then type "moment")')
                elif len(ctx.message.content[7:]) < 5:
                    await ctx.send('sorry, quote triggers must be at least 5 characters.')
                else:
                    await ctx.send(f'next message will be read as quote for \"{ctx.message.content[7:]}\", type CANCEL to cancel this.')
                    self.quote_queue[ctx.message.author.id] = ctx.message.content[7:].lower()
                return

    # quote receptor
    @commands.Cog.listener('on_message')
    async def quote_receptor_adder(self, message):
        if len(self.quote_queue) != 0 and message.author.id in self.quote_queue:
            if message.content == 'CANCEL':
                await message.channel.send('Cancelled!')
                del self.quote_queue[message.author.id]
            else:
                print('ADDING QUOTE', self.quote_queue[message.author.id], message.content)
                self.redis.hset('responses', self.quote_queue[message.author.id], message.content)
                del self.quote_queue[message.author.id]

    # quote responder
    @commands.Cog.listener('on_message')
    async def quote_receptor(self, message):
        response = self.redis.hget('responses', message.content.lower())
        if (response and ((message.author.id not in self.limited)
                          or (message.author.id in self.limited and time.time()-self.limited[message.author.id] > self.limit)
                          or self.limit <= 0)):
            self.limited[message.author.id] = time.time()
            await message.channel.send(response)
        elif response:
            await message.channel.send(f'shut, responses are ratelimited to ***{self.limit}*** seconds', delete_after=1)

    # quote deleter
    @commands.command()
    async def del_quote(self, ctx):
        for role in ctx.message.author.roles:
            if role.name == 'Mods' or role.name == 'Admins' or ctx.author.id == 132620792818171905:
                trigger = ctx.message.content[11:].lower()
                if self.redis.hget('responses', trigger):
                    self.redis.hdel('responses', trigger)
                    await ctx.send(f'trigger "{trigger}" was deleted.')
                else:
                    await ctx.send(f'sorry, trigger "{trigger}" wasn\'t found.')
                return

    # Ratelimit setter
    @commands.command()
    async def ltds(self, ctx, arg):
        if arg:
            try:
                limit = int(arg)
            except ValueError:
                await ctx.send('sorry, please provide a valid number.')
            if limit < 0:
                await ctx.send('sorry, please provide a positive value.')
            else:
                self.limit = limit
                await ctx.send(f'quote trigger limit set to ***{self.limit}*** seconds!')

    # Ratelimit toggler
    @commands.command()
    async def ltd(self,ctx):
        if self.limit == 0:
            self.limit = 60
            await ctx.send(f'*slow down,* ratelimit set to ***{self.limit}***')
        elif self.limit > 0:
            self.limit = self.limit*(-1)
            await ctx.send('***BRAKES OFF*** <:based:620490020536451072>')
        else:
            self.limit = self.limit*(-1)
            await ctx.send(f'*slow down,* ratelimit set to ***{self.limit}***')


def setup(client):
    client.add_cog(quotes(client))
