import discord
import os # get .env token
from dotenv import load_dotenv #abstract your discord bot's token from .env file
from discord.ext import commands # command to print the embed_welcome_message
from discord.utils import get #get your guild id, member id and role id. So we can add role to that memeber
from discord import app_commands
import asyncio

# IF SLASH COMMAND NOT WORKING, right-click your bot, click into "app" and click "manage server integration" you can see your command there give the command modify command permission
# Don't forget you need to create a .env file yourself, and use the token you obtain from the discord bot website.

load_dotenv()
token = os.getenv('TOKEN')
intents = discord.Intents.all() #receive message content
intents.members = True 
intents.message_content = True  
intents.reactions = True 
bot = commands.Bot(command_prefix = "!", intents = intents) #command, when user input !react_role to print the welcome message and enable the react role function

channel_id = 2# replace with your channel id, just write the number, etc 123456789
GUILD_ID = discord.Object(id=) #replace your guild_ID
embed_welcome_message = discord.Embed(title="歡迎來到本DC群！", description="新成員請點擊以下反應來獲得身分組", color=discord.Color.blue())
react_role_mapping = {
    "👍": "guest",
    }
welcome_message_id = "" # save your welcome_message_id, so we can know which message's emoji reaction we need to listen to.

@bot.event
async def on_ready(): # check whether your bot online and check whether the embed_welcome_message already existed or not.
    global welcome_message_id
    print(f"bot name: {bot.user}")
    print("the channel id is:",channel_id)
    try:
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"synced {len(synced)} commands")
    except:
        print("cannot synced slash command")
    try :
        channel = bot.get_channel(channel_id)
        if channel:
            print("channel found!")
        else:
            print("channel not found, please enter the correct channel_id")
    except Exception as e:
        print("Error!", e)
    await asyncio.sleep(2) # wait for finding the message we want, i think it will work maybe.
    async for msg in channel.history(limit=20):
        if msg.embeds:
            embeded_contents = msg.embeds[0]
            if embeded_contents.title == "歡迎來到本DC群！":
                print(f"Found welcome message with ID: {msg.id}")
                welcome_message_id = msg.id
                break
            else:
                print("no message")
    else:
        print("welcome message not found in last 20 message")
    if welcome_message_id:
        await process_existing_reactions()
        
async def process_existing_reactions():
    print("process_existing_reactions functioning")
    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            print("Channel not found")
            return

        # Fetch the message with its reactions
        message = await channel.fetch_message(welcome_message_id)
        guild = message.guild

        print(f"assigning role to the user.")
   
        for reaction in message.reactions:
            emoji = reaction.emoji
            try:
                react_role_mapping[emoji]
            except:
                print(f'emoji \"{emoji}\" do not have a corresponding role')
                continue
            role_name = react_role_mapping[emoji]
            async for user in reaction.users():
                if user.id == bot.user.id:  # Skip bot
                    continue
                member = guild.get_member(user.id)
                if not member:
                    print(f"User {user} not found in server") # will it happen? idk
                    continue
                role = get(guild.roles, name=role_name)
                if not discord.utils.get(member.roles, id=role.id):
                    try:
                        await member.add_roles(role)
                        print(f'assgined role \"{role}\" to memeber \"{member.display_name}\"')
                    except Exception as e:
                        print(f"Failed to assign role: {e}")
                else:
                    print(f'member \"{member.display_name}\" already contain the role \"{role}\"')

    except Exception as e:
        print(f"Error processing reactions: {e}")   
        
@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id) #get guild id
    member = get(guild.members, id=payload.user_id) # get guild's member name
    if payload.channel_id == channel_id and payload.message_id == welcome_message_id: #specify the message you want to listen to
        emoji = str(payload.emoji)
        try:
            react_role_mapping[emoji]
        except:
            print(f'emoji \"{emoji}\" do not have a corresponding role')
        try:
            role_name = react_role_mapping[emoji]
            role = get(guild.roles, name=role_name) # get your guild's role
        except:
            print(f"Role '{role_name}' not found")
        if role:
            if not discord.utils.get(member.roles, id=role.id):
                try:
                    await member.add_roles(role)
                    print(f'assgined role \"{role}\" to memeber \"{member.display_name}\"')
                except Exception as e:
                    print(f"Failed to assign role: {e}")
            else:
                print(f'member \"{member.display_name}\" already contain the role \"{role}\"')
            
    else:
        print("channel_id or message_id not found.")
        
@bot.hybrid_command(name="react_role", description="歡迎訊息,成員可以用emoji來獲得身份組",guild=GUILD_ID) # or call the command by !react_role
#@bot.tree.command(name="react_role", description="歡迎訊息,成員可以用emoji來獲得身份組",guild=GUILD_ID)
async def react_role(ctx):
    global welcome_message_id
    message = await ctx.send(embed=embed_welcome_message)
    for emoji in react_role_mapping:
        await message.add_reaction(emoji)
    print("you have used the command! the new welcome_message id is:", message.id)
    welcome_message_id = message.id

bot.run(token)
