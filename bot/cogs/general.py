import discord
from discord.ext import commands
import logging

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('General Cog loaded.')

    @commands.command(name='ping', help='Responds with Pong! and latency.')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 ({latency}ms)')

    WELCOME_CHANNEL_ID = 1441028094688493690 # Replace with your actual channel ID
    WELCOME_MESSAGE_TEMPLATE = "{user.mention} wellcome to north corea"

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f'{member} has joined the server.')
        if self.WELCOME_CHANNEL_ID:
            welcome_channel = self.bot.get_channel(self.WELCOME_CHANNEL_ID)
            if welcome_channel:
                welcome_message = self.WELCOME_MESSAGE_TEMPLATE.format(user=member)
                await welcome_channel.send(welcome_message)
                logging.info(f'Sent welcome message to {welcome_channel.name} for {member}.')
            else:
                logging.warning(f'Welcome channel with ID {self.WELCOME_CHANNEL_ID} not found.')

async def setup(bot):
    await bot.add_cog(General(bot))
