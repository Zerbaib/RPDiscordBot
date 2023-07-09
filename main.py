import disnake
from disnake.ext import commands
import os
import json
import asyncio

data_file_path = 'data/users.json'
config_file_path = 'config.json'
config_data = {
    "TOKEN": "your_bot_token",
    "LOG_ID": 1234567890,
    "YOUR_ID": 1234567890,
    "sec_loop": 60,
    "del_time": 3
}

if not os.path.exists(data_file_path):
    with open(data_file_path, 'w') as users_file:
        users_file.write('[]')

if not os.path.exists(config_file_path):
    with open(config_file_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
else:
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)

token = config["TOKEN"]
log_chan = config["LOG_ID"]
you = config["YOUR_ID"]
sec_loop = config["sec_loop"]
del_time = config["del_time"]

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())

@bot.event
async def on_ready():
    await status_loop()
    print(f'Logged in as {bot.user.name}')

def save_users(user):
    with open(data_file_path, 'w') as users_file:
        json.dump(user, users_file, indent=4, ensure_ascii=False)

async def status_loop():
    while not bot.is_closed():
        with open(data_file_path, 'r') as users_file:
            users = json.load(users_file)

        users_count = len(users)
        activity = disnake.Activity(
            type=disnake.ActivityType.watching,
            name=f'{users_count} Users'
        )
        await bot.change_presence(activity=activity)

        await asyncio.sleep(sec_loop)

bot.loop.create_task(status_loop())
bot.run(token)