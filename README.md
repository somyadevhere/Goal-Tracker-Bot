# Goal Tracker Telegram Bot

## Features
- Create daily tasks
- Track your progress
- Earn and lose points based on task completion
- Maintain a streak of completed tasks

## Prerequisites
- Python 3.7+
- Telegram account
- Telegram Bot Token from BotFather

## Setup Instructions

1. **Create a Telegram Bot**
   - Open Telegram and search for @BotFather
   - Send `/newbot` to create a new bot
   - Follow the instructions to name your bot
   - Save the bot token you receive

2. **Set Up the Project**
   ```bash
   # Clone the repository
   git clone https://github.com/somyadevhere/Goal-Tracker-Bot
   cd goal-tracker-bot

   # Create a virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure the Bot**
   - Open `goal_tracker_bot.py`
   - Replace `'YOUR_BOT_TOKEN'` with the token you received from BotFather

4. **Run the Bot**
   ```bash
   python goal_tracker_bot.py
   ```

## Bot Commands
- `/start` - Initialize your account
- `/addtask` - Add a new daily task
- `/mytasks` - View today's tasks
- `/points` - Check your current points
- `/help` - Show help message

## How It Works
- When you add a task, you'll get buttons to mark it as completed or failed
- Completed tasks: +100 points
- Failed tasks: -110 points
- Tracks your daily progress and motivation

## Database
- Uses SQLite to store user information and tasks
- Automatically creates `goal_tracker.db` file

## Customization
- Modify point system in the `complete_task()` and `fail_task()` methods
- Adjust database schema in `create_tables()` method

## Troubleshooting
- Ensure you have the latest version of dependencies
- Check that your bot token is correct
- Make sure you have an active internet connection

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
