import disnake
from disnake.ext import commands
import os
import json
import asyncio
from datetime import datetime

data_file_path = 'users.json'
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

def save_users(users):
    with open(data_file_path, 'w') as users_file:
        json.dump(users, users_file, indent=4, ensure_ascii=False)

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

@bot.slash_command(
    name="cree",
    description="Crée ton profil RP."
)
async def cree(ctx: disnake.ApplicationCommandInteraction, prenom: str, nom: str, naissance: str):
    author = ctx.author.id
    channel = await bot.fetch_channel(log_chan)

    with open(data_file_path, 'r') as users_file:
        users = json.load(users_file)

    existing_user = next((s for s in users if str(s['user_id']).lower() == str(author).lower()), None)
    if existing_user:
        await ctx.send("Users already in the database.", delete_after=del_time)
        return

    try:
        day, month, year = map(int, naissance.split('/'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError
    except (ValueError, AttributeError):
        await ctx.send("Invalid birthdate format. Please use the format: dd/mm/yyyy.", delete_after=del_time)
        return
    
    new_user = {
        "user_id": author,
        "name": prenom,
        "last_name": nom,
        "birthdate": naissance,
        "job": None
    }
    users.append(new_user)
    save_users(users)

    embed = disnake.Embed(
        title="Your profile as been created !",
        description=f"With option:\n"
                    f"**Name**: ``{prenom}``\n"
                    f"**Last Name**: ``{nom}``\n"
                    f"**Birthdate**: ``{naissance}``\n",
        color=disnake.Color.dark_green()
    )
    embed.set_footer(text=f"Executed at {datetime.now().strftime('%H:%M:%S %Y-%m-%d')}")
    
    await ctx.send(embed=embed)
    embed = disnake.Embed(
        title="A profile as been created !",
        description=f"Option of account:\n"
                    f"**Name**: ``{prenom}``\n"
                    f"**Last Name**: ``{nom}``\n"
                    f"**Birthdate**: ``{naissance}``\n"
                    f"**Job**: ``Null``",
        color=disnake.Color.dark_green()
    )
    embed.set_footer(text=f"Created at {datetime.now().strftime('%H:%M:%S %Y-%m-%d')}")
    await channel.send(embed=embed)
    save_users(users)

bot.loop.create_task(status_loop())
bot.run(token)