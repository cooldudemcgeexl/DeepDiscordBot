
# bot.py
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Loads user token for bot from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    print("No token found. Please check that the API token has been inserted into .env")
    exit(0)


bot = commands.Bot(command_prefix='!')

# Initializing chance of message to 3%, interjections to true
msgChanceUbound = 33
interjectionsEnabled = True

@bot.command(name = 'interject', help = 'Enables/Disables random interjections', pass_context = True)
async def toggleInterjections(ctx):
    global interjectionsEnabled
    interjectionsEnabled = not interjectionsEnabled
    if interjectionsEnabled:
        statusMsg = "Interjections enabled."
    else:
        statusMsg = "Interjections disabled."
    await ctx.send(statusMsg)
    return


@bot.command(name='change_freq', help = "Changes the frequency of this bot's messages", pass_context=True)
async def changeFrequency(ctx, newFreq):
    # Allows users to adjust frequency of messages sent by the bot
    global msgChanceUbound
    msgChanceUbound = int((1/int(newFreq))*100)
    print(f"Message chance changed to: {newFreq} %\n")
    await ctx.send(f"Chance of a message is now {newFreq}%")
    return

@bot.command(name='reload_knowledge', help = "Refreshes the bot's knowledge base")
async def reload_CSV(ctx):
    # Refreshes quote list. Useful if changing csv file without restarting bot. 
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
    # Writes to console/text file time, date, location, and contents of message sent by bot
    if message.author == bot.user:
        statusString = "[" + str(message.created_at) + "] Message sent in channel (" + message.channel.name + ") on server (" + message.channel.guild.name + "): " + message.content + "\n"
        print(statusString)
        log_object = open('log.txt','a',encoding = 'utf-8')
        log_object.write(statusString)
        log_object.close()
        return

    # Bot will pull a random message if mentioned.
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        await message.channel.send(pull_rand_csv())
        return


    # Random chance between 1 and ubound to send a message.
    # This causes bot to randomly interject when messages are sent.
    global interjectionsEnabled
    msgChance = random.randint(1,msgChanceUbound)
    if (msgChance == 1) and interjectionsEnabled:
        await message.channel.send(pull_rand_csv())


    await bot.process_commands(message)


def pull_rand_csv():
    # Reads a random line from the quote list and returns the message to be sent
    randline = random.randint(0,numrows)
    msgtext = allquotes[randline]

    # Removing quotes, comma, and newline. These will always occupy the same positions in the string.
    msgtext = msgtext[1:-3]
    return msgtext

def file_len(fname):
    with open(fname, encoding='utf-8') as f:
        for i, l in enumerate(f):
            pass
    f.close()
    return i + 1


# Initializing values for bot, this will be moved into proper structure later

file = "outputtext.csv"
numrows = file_len(file)
quotefile = open(file, "r", encoding = 'utf-8')
allquotes = quotefile.readlines()
quotefile.close()
random.seed()


bot.run(TOKEN)
