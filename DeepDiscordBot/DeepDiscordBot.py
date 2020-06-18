
# bot.py
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    print("No token found. Please check that the API token has been inserted into .env")
    exit(0)

# client = discord.Client()
bot = commands.Bot(command_prefix='!')

msgChanceUbound = 33




@bot.command(name='change_freq', help = "Changes the frequency of this bot's messages", pass_context=True)
async def changeFrequency(ctx, newFreq):
    global msgChanceUbound
    msgChanceUbound = int((1/int(newFreq))*100)
    print(f"Message chance changed to: {newFreq} %\n")
    await ctx.send(f"Chance of a message is now {newFreq}%")
    return

@bot.command(name='reload_knowledge', help = "Refreshes the bot's knowledge base")
async def reload_CSV(ctx):
    global allquotes
    quotefile = open(file, "r", encoding = 'utf-8')
    allquotes = quotefile.readlines()
    quotefile.close()
    await ctx.send("Knowledge updated.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        statusString = "[" + str(message.created_at) + "] Message sent in channel (" + message.channel.name + ") on server (" + message.channel.guild.name + "): " + message.content + "\n"
        print(statusString)
        log_object = open('log.txt','a',encoding = 'utf-8')
        log_object.write(statusString)
        log_object.close()
        return

    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        await message.channel.send(pull_rand_csv())
        return

    msgChance = random.randint(1,msgChanceUbound)
    if msgChance == 1:
        await message.channel.send(pull_rand_csv())


    await bot.process_commands(message)


def pull_rand_csv():
    randline = random.randint(0,numrows)
    msgtext = allquotes[randline]
    msgtext = msgtext.rstrip(',\n')
    msgtext = msgtext.strip('\"')


    return msgtext

def file_len(fname):
    with open(fname, encoding='utf-8') as f:
        for i, l in enumerate(f):
            pass
    f.close()
    return i + 1


file = "outputtext.csv"
numrows = file_len(file)
quotefile = open(file, "r", encoding = 'utf-8')
allquotes = quotefile.readlines()
quotefile.close()
random.seed()


bot.run(TOKEN)
