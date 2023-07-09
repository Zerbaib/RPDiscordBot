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
        await ctx.send("Tu a deja crée ton profil.", delete_after=del_time)
        return

    try:
        day, month, year = map(int, naissance.split('/'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError
    except (ValueError, AttributeError):
        await ctx.send("Le format de la date est invalide utilise: ``dd/mm/yyyy``.", delete_after=del_time)
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
        title="Ton profil a bien ete crée !",
        description=f"Avec les option:\n"
                    f"**Prénom**: ``{prenom}``\n"
                    f"**Nom**: ``{nom}``\n"
                    f"**Date de naissance**: ``{naissance}``\n",
        color=disnake.Color.dark_green()
    )
    embed.set_footer(text=f"Executer a {datetime.now().strftime('%H:%M:%S %Y-%m-%d')}")
    
    await ctx.send(embed=embed)
    embed = disnake.Embed(
        title="Un profil a ete crée !",
        description=f"Option du compte:\n"
                    f"**Prénom**: ``{prenom}``\n"
                    f"**Nom**: ``{nom}``\n"
                    f"**Date de naissance**: ``{naissance}``\n"
                    f"**Travail**: ``Null``",
        color=disnake.Color.dark_green()
    )
    embed.set_footer(text=f"Crée a {datetime.now().strftime('%H:%M:%S %Y-%m-%d')}")
    await channel.send(embed=embed)
    save_users(users)

@bot.slash_command(
    name="whois",
    description="Regarde le profil d'un utilisateur."
)
async def whois(ctx: disnake.ApplicationCommandInteraction, user: disnake.User = None):
    if user is None:
        user = ctx.author

    with open(data_file_path, 'r') as users_file:
        users = json.load(users_file)

    selected_user = next((s for s in users if str(s['user_id']) == str(user.id)), None)
    if not selected_user:
        embed = disnake.Embed(
        title=f"Le profil de {user.display_name} n'a pas ete trouver",
        description=f"**{user.display_name}** dois executer\n"
                    f"la commande **``/cree``**\n"
                    f"Pour crée sont profil",
        color=disnake.Color.blue()
        )
        await ctx.send(embed=embed)
        return

    name = selected_user.get("name")
    last_name = selected_user.get("last_name")
    birthdate = selected_user.get("birthdate")
    job = selected_user.get("job")

    if job is None:
        job = "N'a pas de travail."

    embed = disnake.Embed(
        title=f"Profil de: {name} aka ``{user.display_name}``",
        description=f"**Prénom**: {name}\n"
                    f"**Nom**: {last_name}\n"
                    f"**Date de naissance**: {birthdate}\n"
                    f"**Travail**: {job}\n",
        color=disnake.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.slash_command(
    name="addjob",
    description="Ajoute le travail de quelqu'un"
)
@commands.has_permissions(administrator=True)
async def add_job(ctx: disnake.ApplicationCommandInteraction, job: str, user: disnake.User = None):
    channel = await bot.fetch_channel(log_chan)
    if user is None:
        user = ctx.author
    with open(data_file_path, 'r') as users_file:
        users = json.load(users_file)

    selected_user = next((s for s in users if str(s['user_id']) == str(user.id)), None)
    if not selected_user:
        embed = disnake.Embed(
            title=f"Utilisateur introuvable",
            description=f"L'utilisateur {user} n'a pas été trouvé.",
            color=disnake.Color.dark_red()
        )
        await ctx.send(embed=embed)
        return

    selected_user['job'] = job
    save_users(users)

    embed = disnake.Embed(
        title=f"Travail ajouté avec succès",
        description=f"Le travail de {user} a été mis à jour.\n"
                    f"**Nouveau travail**: {job}",
        color=disnake.Color.dark_green()
    )
    await ctx.send(embed=embed)
    embed = disnake.Embed(
        title=f"Un travail a ete ajouter",
        description=f"Le travail de {user} a été mis à jour.\n"
                    f"**Nouveau travail**: ``{job}``",
        color=disnake.Color.dark_green()
    )
    await channel.send(embed=embed)

@bot.slash_command(
    name="deleteprofile",
    description="Supprime le profil d'un utilisateur"
)
@commands.has_permissions(administrator=True)
async def delete_profile(ctx: disnake.ApplicationCommandInteraction, user: disnake.User):
    channel = await bot.fetch_channel(log_chan)
    
    with open(data_file_path, 'r') as users_file:
        users = json.load(users_file)

    selected_user = next((s for s in users if str(s['user_id']) == str(user.id)), None)
    if not selected_user:
        embed = disnake.Embed(
            title=f"Utilisateur introuvable",
            description=f"L'utilisateur {user} n'a pas été trouvé.",
            color=disnake.Color.dark_red()
        )
        await ctx.send(embed=embed)
        return

    users.remove(selected_user)
    save_users(users)

    embed = disnake.Embed(
        title=f"Profil supprimé avec succès",
        description=f"Le profil de {user} a été supprimé.",
        color=disnake.Color.dark_red()
    )
    await ctx.send(embed=embed)

    log_embed = disnake.Embed(
        title="Profil supprimé",
        description=f"Profil supprimé par l'administrateur {ctx.author.mention}\n"
                    f"**Utilisateur**: {user.mention}\n"
                    f"**Prénom**: {selected_user['name']}\n"
                    f"**Nom**: {selected_user['last_name']}\n"
                    f"**Date de naissance**: {selected_user['birthdate']}\n"
                    f"**Travail**: {selected_user['job']}\n",
        color=disnake.Color.dark_red()
    )
    await channel.send(embed=log_embed)

bot.loop.create_task(status_loop())
bot.run(token)