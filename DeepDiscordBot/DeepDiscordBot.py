
# bot.py
import os
import random
import asyncio
import discord
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

# Loads user token for bot from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    print("No token found. Please check that the API token has been inserted into .env")
    exit(0)

# Loads file paths from .env
inputText = os.getenv('QUOTE_INPUT')
if inputText is None:
    print("No input file found, please set up .env file")
    exit(0)

outputfile = os.getenv('OUTPUT_FILE')
if outputfile is None:
    outputfile = "log.txt"

cmdPrefix = os.getenv('COMMAND_PREFIX')
if cmdPrefix is None:
    cmdPrefix = '!'

bot = commands.Bot(command_prefix=cmdPrefix)


# Initializing chance of message, interjections, and repeats based on values in .env
msgChanceUbound = int(os.getenv('DEFAULT_MESSAGE_UBOUND'))
interjectionsEnabled = bool(os.getenv('INTERJECT'))
repeatsEnabled = bool(os.getenv('REPEATS'))
ttsEnabled = bool(os.getenv("TTS"))

@bot.command(name='tts', help = 'Toggles text-to-speech', pass_context = True)
async def toggleTTS(ctx):
    global ttsEnabled
    ttsEnabled = not ttsEnabled
    if ttsEnabled:
        statusMsg = "TTS enabled."
    else:
        statusMsg = "TTS disabled."
    await ctx.send(statusMsg)
    return

@bot.command(name='repeat', help='Toggles repeating messages', pass_context = True)
async def toggleRepeats(ctx):
    global repeatsEnabled
    repeatsEnabled = not repeatsEnabled
    if repeatsEnabled:
        statusMsg = "Repeats enabled."
    else:
        statusMsg = "Repeats disabled."
    await ctx.send(statusMsg)
    return

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
async def refresh_Quotes(ctx):
    # Refreshes quote list. Useful if changing csv file without restarting bot. 
    reload_CSV()
    await ctx.send("Knowledge updated.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(random_send())

@bot.event
async def on_message(message):
    # Writes to console/text file time, date, location, and contents of message sent by bot
    if message.author == bot.user:
        statusString = "[" + str(message.created_at) + "] Message sent in channel (" + message.channel.name + ") on server (" + message.channel.guild.name + "): " + message.content + "\n"
        print(statusString)
        log_object = open(outputfile,'a',encoding = 'utf-8')
        log_object.write(statusString)
        log_object.close()
        return

    # Bot will pull a random message if mentioned.
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        await message.channel.send(pull_rand_csv(),tts=ttsEnabled)
        return


    # Random chance between 1 and ubound to send a message.
    # This causes bot to randomly interject when messages are sent.
    global interjectionsEnabled
    msgChance = random.randint(1,msgChanceUbound)
    if (msgChance == 1) and interjectionsEnabled:
        await message.channel.send(pull_rand_csv(),tts=ttsEnabled)


    await bot.process_commands(message)

# Sends a random message after waiting 
async def random_send():
    await bot.wait_until_ready()
    while not bot.is_closed():
        # Pulls random channel from random guild
        global interjectionsEnabled
        randServer = random.choice(bot.guilds)
        randChannel = random.choice(randServer.text_channels)
        await asyncio.sleep(random.randint(1,20)*10000) # Between 10000 and 200000 seconds
        try:
            if interjectionsEnabled:
                await randChannel.send(pull_rand_csv(),tts=ttsEnabled)
        except:
            
            print("[" + str(datetime.now()) + "] Channel access denied in channel (" + randChannel.name + ")")


def pull_rand_csv():
    
    if len(allquotes) == 0:
        reload_CSV()
    # Reads a random line from the quote list and returns the message to be sent
    randline = random.randint(0,len(allquotes)-1)
    global repeatsEnabled
    # Pops from quotes array to prevent repeats
    if repeatsEnabled:
        msgtext = allquotes[randline]
    else:
        msgtext = allquotes.pop(randline)
    # Removing quotes, comma, and newline. These will always occupy the same positions in the string.
    msgtext = msgtext[1:-3]
    return msgtext

# Reloads quote list from file
def reload_CSV():
    global allquotes
    quotefile = open(inputText, "r", encoding = 'utf-8')
    allquotes = quotefile.readlines()
    quotefile.close()


quotefile = open(inputText, "r", encoding = 'utf-8')
allquotes = quotefile.readlines()
quotefile.close()
random.seed()



bot.run(TOKEN)