import os
import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

# Replace 'YOUR_BOT_TOKEN' with the actual bot token from BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
class DatabaseManager:
    def __init__(self, db_name='goal_tracker.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Users table to store user information and points
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_points INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0
            )
        ''')
        
        # Tasks table to track daily tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_description TEXT,
                is_completed BOOLEAN DEFAULT 0,
                date_assigned DATE,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        self.conn.commit()

    def create_or_update_user(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, total_points) 
            VALUES (?, ?, 0)
        ''', (user_id, username))
        self.conn.commit()

    def add_daily_task(self, user_id, task_description):
        cursor = self.conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            INSERT INTO tasks (user_id, task_description, is_completed, date_assigned)
            VALUES (?, ?, 0, ?)
        ''', (user_id, task_description, today))
        self.conn.commit()
        return cursor.lastrowid

    def complete_task(self, task_id):
        cursor = self.conn.cursor()
        # Update task completion status
        cursor.execute('''
            UPDATE tasks 
            SET is_completed = 1 
            WHERE task_id = ?
        ''', (task_id,))
        
        # Add points to user
        cursor.execute('''
            UPDATE users 
            SET total_points = total_points + 100, 
                current_streak = current_streak + 1
            WHERE user_id = (SELECT user_id FROM tasks WHERE task_id = ?)
        ''', (task_id,))
        self.conn.commit()

    def fail_task(self, task_id):
        cursor = self.conn.cursor()
        # Subtract points from user
        cursor.execute('''
            UPDATE users 
            SET total_points = total_points - 110, 
                current_streak = 0
            WHERE user_id = (SELECT user_id FROM tasks WHERE task_id = ?)
        ''', (task_id,))
        self.conn.commit()

    def get_user_points(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT total_points FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_today_tasks(self, user_id):
        cursor = self.conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT task_id, task_description 
            FROM tasks 
            WHERE user_id = ? AND date_assigned = ? AND is_completed = 0
        ''', (user_id, today))
        return cursor.fetchall()

# Initialize database
db_manager = DatabaseManager()

# Bot command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Create user in database if not exists
    db_manager.create_or_update_user(user_id, username)
    
    welcome_text = (
        f"Welcome {username}! 🎯\n\n"
        "This bot helps you track and achieve your daily goals. "
        "Here are some commands you can use:\n"
        "/addtask - Add a new daily task\n"
        "/mytasks - View today's tasks\n"
        "/points - Check your current points\n"
        "/help - Show this help message"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['addtask'])
def add_task(message):
    bot.reply_to(message, "Please enter the description of your daily task:")
    bot.register_next_step_handler(message, process_task_description)

def process_task_description(message):
    user_id = message.from_user.id
    task_description = message.text
    
    # Add task to database
    task_id = db_manager.add_daily_task(user_id, task_description)
    
    # Create inline keyboard for task management
    markup = types.InlineKeyboardMarkup()
    complete_button = types.InlineKeyboardButton("✅ Task Completed", callback_data=f'complete_{task_id}')
    fail_button = types.InlineKeyboardButton("❌ Task Failed", callback_data=f'fail_{task_id}')
    markup.row(complete_button, fail_button)
    
    bot.reply_to(message, f"Task added: {task_description}\nMark when done or failed:", reply_markup=markup)

@bot.message_handler(commands=['mytasks'])
def show_tasks(message):
    user_id = message.from_user.id
    tasks = db_manager.get_today_tasks(user_id)
    
    if not tasks:
        bot.reply_to(message, "No active tasks for today!")
        return
    
    tasks_text = "Your tasks for today:\n"
    markup = types.InlineKeyboardMarkup()
    
    for task_id, task_description in tasks:
        tasks_text += f"- {task_description}\n"
        complete_button = types.InlineKeyboardButton("✅ Complete", callback_data=f'complete_{task_id}')
        fail_button = types.InlineKeyboardButton("❌ Failed", callback_data=f'fail_{task_id}')
        markup.row(complete_button, fail_button)
    
    bot.reply_to(message, tasks_text, reply_markup=markup)

@bot.message_handler(commands=['points'])
def show_points(message):
    user_id = message.from_user.id
    points = db_manager.get_user_points(user_id)
    bot.reply_to(message, f"Your current points: {points} 🏆")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith('complete_'):
        task_id = int(call.data.split('_')[1])
        db_manager.complete_task(task_id)
        bot.answer_callback_query(call.id, "Congratulations! 🎉 +100 points")
    
    elif call.data.startswith('fail_'):
        task_id = int(call.data.split('_')[1])
        db_manager.fail_task(task_id)
        bot.answer_callback_query(call.id, "Task failed. -110 points 😔")

# Additional helper commands
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "Goal Tracker Bot Commands:\n"
        "/start - Start the bot and create your account\n"
        "/addtask - Add a new daily task\n"
        "/mytasks - View today's tasks\n"
        "/points - Check your current points\n"
        "/help - Show this help message\n\n"
        "How it works:\n"
        "- Add daily tasks with /addtask\n"
        "- Complete tasks to earn 100 points\n"
        "- Fail tasks and lose 110 points\n"
        "- Keep track of your progress and stay motivated! 💪"
    )
    bot.reply_to(message, help_text)

# Start the bot
def main():
    print("Bot is running...")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()

# Requirements (create a requirements.txt file with these):
# pyTelegramBotAPI
# sqlite3
