# Discord Bot

A feature-rich Discord bot built with discord.py using the command framework.

## Features

- Command-based architecture with cogs
- Environment variable configuration
- Logging system
- Slash command support
- Database integration with SQLAlchemy
- AI integration with Google Generative AI
- Scheduled tasks with APScheduler

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Fill in your Discord bot token and other environment variables.

4. Run the bot:
```bash
python main.py
```

## Project Structure

```
discord/
├── bot/
│   ├── cogs/          # Bot commands and features
│   ├── database/       # Database models and connections
│   └── utils/          # Utility functions
├── config/             # Configuration files
├── data/              # Data files
├── tests/             # Unit tests
├── main.py            # Main bot file
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Environment Variables

Required environment variables:
- `DISCORD_TOKEN`: Your Discord bot token

## Commands

- `!help`: Show all available commands
- Prefix commands: Use `!` or mention the bot

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.