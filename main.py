import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Load Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

    async def setup_hook(self):
        # Load Extensions (Cogs)
        for filename in os.listdir('./bot/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'bot.cogs.{filename[:-3]}')
                logging.info(f'Loaded extension: {filename}')
        
        # Sync commands (for slash commands)
        # await self.tree.sync() 
        logging.info("Bot setup complete.")

    async def on_ready(self):
        logging.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logging.info('------')

bot = MyBot()

if __name__ == '__main__':
    if not TOKEN:
        logging.error("DISCORD_TOKEN not found in .env file.")
    else:
        bot.run(TOKEN)
