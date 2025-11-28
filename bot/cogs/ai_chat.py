import os
import discord
from discord.ext import commands
import google.generativeai as genai
import logging
from collections import defaultdict
import asyncio

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Persona Definitions (System Prompts)
PERSONAS = {
    "kim_jong_un": """
    You are Kim Jong Un, the Supreme Leader of North Korea. 
    Style: Authoritative, anti-imperialist, mentions 'Juche', 'North Korea', and 'Nuclear power'.
    Constraint: Answer in 1 or 2 short sentences. Be firm and proud.
    """,
    "putin": """
    You are Vladimir Putin, President of Russia.
    Style: Stoic, strategic, calm, mentions 'Mother Russia', formal but firm.
    Constraint: Answer in 1 or 2 short sentences.
    """,
    "trump": """
    You are Donald Trump, former US President.
    Style: Hyperbolic, uses capitalized words like 'HUGE', 'SAD', 'FAKE NEWS'. 
    Constraint: Answer in 1 or 2 short sentences. Very confident.
    """,
    "catgirl": """
    You are a cute Catgirl maid.
    Style: Ends sentences with 'nya~', calls user 'Master', uses emojis like 😸.
    Constraint: Answer in 1 or 2 short sentences. Be cute and submissive.
    """,
    "code_teacher": """
    You are a strict Code Teacher.
    Style: No fluff, no greetings. Only code or direct explanations.
    Constraint: Answer in 1 or 2 short sentences (unless providing a code block). Be precise.
    """,
    "emotional_assistant": """
    You are an Empathetic Emotional Assistant.
    Style: Warm, supportive, asks about feelings, validates emotions.
    Constraint: Answer in 1 or 2 short sentences. Be kind.
    """,
    "fool": """
    You are a Fool/Jester.
    Style: Confused, nonsensical, simple-minded, funny.
    Constraint: Answer in 1 or 2 short sentences. Don't make sense.
    """,
    "doctor": """
    You are a Professional Medical Doctor (AI).
    Style: Concise, direct, clinical. NO fluff, NO greetings, NO chat.
    Constraint: Max 50 words per response. 1-4 short sentences only.
    Protocol:
    1. Ask specific questions if symptoms are vague.
    2. Give direct differential diagnosis or medical advice.
    3. Always end with: "Disclaimer: Consult a real doctor."
    """
}

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logging.warning("GOOGLE_API_KEY not found in environment variables. AI Chat will not work.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('models/gemini-flash-lite-latest')

        # Store chat history per channel: {channel_id: chat_session_object}
        self.chat_sessions = {}
        # Store current persona per channel: {channel_id: persona_key}
        self.channel_personas = defaultdict(lambda: "catgirl") 
        # Store auto-chat state: set of channel_ids where auto-chat is enabled
        self.auto_chat_channels = set()

    def _get_chat_session(self, channel_id):
        """Retrieves or creates a chat session for a channel."""
        if channel_id not in self.chat_sessions:
            persona_key = self.channel_personas[channel_id]
            # Map 'meow' to 'catgirl' logic is handled in set_persona, 
            # here we expect valid keys from PERSONAS or default to catgirl
            system_prompt = PERSONAS.get(persona_key, PERSONAS["catgirl"])
            
            # Create a new chat session with the system prompt injected into history
            try:
                 model_with_instruction = genai.GenerativeModel(
                     'models/gemini-flash-lite-latest',
                     system_instruction=system_prompt
                 )
                 self.chat_sessions[channel_id] = model_with_instruction.start_chat(history=[])
            except Exception as e:
                logging.error(f"Error creating chat session: {e}")
                return None
        
        return self.chat_sessions[channel_id]

    @commands.command(name="autochat")
    async def toggle_autochat(self, ctx, status: str):
        """Enables or disables auto-reply for all messages. Usage: !autochat on/off"""
        status = status.lower()
        if status == "on":
            self.auto_chat_channels.add(ctx.channel.id)
            await ctx.send(f"🤖 **Auto-chat ENABLED** for this channel! I will reply to every message. (Type `!autochat off` to stop)")
        elif status == "off":
            if ctx.channel.id in self.auto_chat_channels:
                self.auto_chat_channels.remove(ctx.channel.id)
            await ctx.send(f"zzz **Auto-chat DISABLED**. I will only reply when mentioned.")
        else:
            await ctx.send("Usage: `!autochat on` or `!autochat off`")

    @commands.command(name="persona")
    async def set_persona(self, ctx, persona_name: str):
        """Switches the AI persona. Options: kim_jong_un, putin, trump, catgirl (or meow), code_teacher, emotional_assistant, fool."""
        persona_name = persona_name.lower()
        
        # Handle aliases
        if persona_name == "meow":
            persona_name = "catgirl"
            
        if persona_name in PERSONAS:
            self.channel_personas[ctx.channel.id] = persona_name
            # Reset session to apply new persona
            if ctx.channel.id in self.chat_sessions:
                del self.chat_sessions[ctx.channel.id]
            await ctx.send(f"Switched persona to: **{persona_name}**")
        else:
            options = ", ".join(PERSONAS.keys())
            await ctx.send(f"Invalid persona. Options: {options}, meow")

    @commands.command(name="reset")
    async def reset_chat(self, ctx):
        """Resets the conversation history."""
        if ctx.channel.id in self.chat_sessions:
            del self.chat_sessions[ctx.channel.id]
        await ctx.send("Conversation history reset.")

    @commands.command(name="chat")
    async def chat(self, ctx, *, message: str):
        """Chat with the AI."""
        async with ctx.typing():
            try:
                session = self._get_chat_session(ctx.channel.id)
                if not session:
                    await ctx.send("AI is not configured properly (missing API key?).")
                    return

                # Generate response
                response = await session.send_message_async(message)
                await ctx.send(response.text)

            except Exception as e:
                logging.error(f"Gemini API Error: {e}")
                await ctx.send("Oops! Something went wrong with my AI brain.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handles command errors. If a command is not found but the bot was mentioned, treat it as chat."""
        if isinstance(error, commands.CommandNotFound):
            # Check if the message started with a mention of the bot
            if self.bot.user in ctx.message.mentions:
                # It was likely a chat attempt or a persona switch attempt that looked like a command
                # The on_message event should have handled this, but process_commands raises this error first.
                # Actually, process_commands is usually called AFTER on_message if we use bot.process_commands.
                # But if on_message calls process_commands (default behavior if not overridden in main), it happens.
                
                # We can just ignore this error because our on_message logic (if processed) handles the response.
                # OR we can trigger the chat logic here if on_message didn't catch it.
                return 
            
            # If it wasn't a mention (e.g. "!invalidcommand"), we can ignore or log it.
            logging.info(f"Command not found: {ctx.message.content}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent bot from replying to itself or other bots
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)

        # 1. Handle Mentions (Highest Priority)
        if self.bot.user in message.mentions:
            clean_content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Handle "switch persona"
            if any(k in clean_content.lower() for k in ["switch persona", "change persona", "切换角色"]):
                 options = ", ".join(PERSONAS.keys())
                 await message.channel.send(f"Available personas: **{options}, meow**\nType `@BotName <persona>` to switch!")
                 return

            # Handle direct persona switch
            possible_persona = clean_content.lower()
            if possible_persona == "meow": possible_persona = "catgirl"
            if possible_persona in PERSONAS:
                self.channel_personas[message.channel.id] = possible_persona
                if message.channel.id in self.chat_sessions:
                    del self.chat_sessions[message.channel.id]
                await message.channel.send(f"Switched persona to: **{possible_persona}**")
                return

            # Trigger chat
            if clean_content:
                await self.chat(ctx, message=clean_content)
            else:
                await ctx.send("Yes? How can I help you?")
            return 

        # 2. Handle Commands (e.g. !ping, !autochat)
        # If it's a valid command, we let the internal command handler process it.
        # We don't want auto-chat to reply to "!autochat off" with "I don't understand".
        if ctx.valid:
            return 

        # 3. Handle Auto-Chat (Lowest Priority)
        # Reply to everything else if auto-chat is enabled
        if message.channel.id in self.auto_chat_channels:
             await self.chat(ctx, message=message.content)

async def setup(bot):
    await bot.add_cog(AIChat(bot))
