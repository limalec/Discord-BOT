import asyncio
import json
from discord.ext import commands, tasks
import discord
import random
from urllib.request import urlopen
from config import discord_token, author_id

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = author_id  # Change to your discord id

user_message_counts = {}
flood_monitoring_interval = 5 
message_limit = 5 
flood_monitoring_active = False
poll_time_limit = 30

@bot.command()
async def poll(ctx, *, question):
    poll_message2 = f"@here , {ctx.author.mention} has a question : {question}"

    poll_message2 = await ctx.send(poll_message2)
    poll_message = await ctx.send(question)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

    await asyncio.sleep(poll_time_limit)
    poll_message = await ctx.fetch_message(poll_message.id)

    thumbs_up = 0
    thumbs_down = 0
    for reaction in poll_message.reactions:
        if reaction.emoji == "👍":
            thumbs_up = reaction.count - 1 
        elif reaction.emoji == "👎":
            thumbs_down = reaction.count - 1

    results_message = f"Poll is over !\nQuestion : {question}\n👍 : {thumbs_up}\n👎 : {thumbs_down}"

    await poll_message.delete()
    await ctx.send(results_message)

@bot.command()
async def xkcd(ctx):
    random_comic_num = random.randint(1, 2500)
    
    xkcd_url = f"https://xkcd.com/{random_comic_num}/info.0.json"

    try:
        response = urlopen(xkcd_url)
        data = response.read().decode("utf-8")

        img_url = json.loads(data)["img"]

        await ctx.send(f"{img_url}")
    except Exception as e:
        await ctx.send("Error fetching")

@bot.command()
async def flood(ctx):
    global flood_monitoring_active
    if flood_monitoring_active == False:
        flood_monitoring_active = True
        await ctx.send("Message monitoring on")
        clear_message_counts.start()

@tasks.loop(minutes=flood_monitoring_interval)
async def clear_message_counts():
    user_message_counts.clear()

@bot.event
async def on_message(message):
    global flood_monitoring_active
    
    if flood_monitoring_active and message.author != bot.user:
        author_id = message.author.id
        if author_id in user_message_counts:
            user_message_counts[author_id] += 1
        else:
            user_message_counts[author_id] = 1

        if "Alexa, désactive-toi" in message.content:
            flood_monitoring_active = False
            user_message_counts.clear()
            clear_message_counts.stop()
            await message.channel.send("Message monitoring off")
            return
        
        if user_message_counts[author_id] > message_limit:
            await message.channel.send(f"{message.author.mention}, do not spam !")
    await bot.process_commands(message)

@bot.command()
async def name(ctx):
    user = ctx.message.author
    await ctx.send(f"{user.name}")

@bot.command()
async def d6(ctx):
    result = random.randint(1, 6)
    await ctx.send(f"{result}")

@bot.command()
async def admin(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if role is None:
        role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())
    await member.add_roles(role)
    await ctx.send(f"{member.mention} is now Admin.")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=""):
    if reason:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned for the following reason : {reason}")
    else:
        funny_phrases = [
            "Yeet",
            "Bye bye",
            "cy@",
        ]
        random_phrase = random.choice(funny_phrases)

        await member.ban(reason=random_phrase)
        await ctx.send(f"{member.mention} has been banned. {random_phrase}")

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

token = discord_token
bot.run(token)  # Starts the bot