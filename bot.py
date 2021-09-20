import discord
import os
import queue
import re
import time
import urllib.request
import youtube_dl

from discord.ext import commands, tasks
from discord.player import FFmpegPCMAudio
from os.path import exists
from staticvars import APIKEY
from staticvars import YDL_PROPS

#File constants
OS_SEPARATOR= os.path.sep #ensures file separator is correct if using linux shell
SONG_FILE="song.mp3"
PATH_TO_SONG_FILE="." + OS_SEPARATOR + "song.mp3"
FILE_EXTENSION=".mp3"
BASE_DIR_CONSTANT="." + OS_SEPARATOR

#Youtube constants
YT_REQUEST_BASE_URL="https://www.youtube.com/results?search_query="
YT_WATCH_BASE_URL="https://www.youtube.com/watch?v="

#queue of songs
QUEUE=queue.Queue()

#prefix to signal the bot to listen to the command
client = commands.Bot(command_prefix= '!', )

#state variable in rare cases where the song is loaded and you hit the idle timer perfectly
queue_is_empty=True

### Starting message to give some feedback that bot has started
@client.event
async def on_ready():
    print('Starting bot with user: {0.user}'.format(client))


################ COMMANDS ##################

### Main play command that pulls bot into channel and plays song also starts the recursive queue playing
@client.command(pass_context = True)
async def play(ctx, *, arg):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice and ctx.message.author.voice.channel != voice.channel):
        print("can't play songs while user is not in same channel as bot")
        return
    url = getYTURL(arg)
    #if a song is playing or queue is already filled up, add to the back of queue
    if voice != None and (QUEUE.qsize() >= 1 or voice.is_playing()):
        await ctx.send("added: " + url + " to the queue")
    QUEUE.put(url)
    global queue_is_empty
    queue_is_empty=False

    if(voice == None or not voice.is_playing()):
        try:
            #check if bot is in current channel, move it if needed
            if(ctx.author.voice):
                channel = ctx.message.author.voice.channel
                if(voice == None):
                    voice = await channel.connect()
                    if(not leaveLoop.is_running()):
                        leaveLoop.start(voice, ctx)
            playNext(ctx)

            #give user feedback with embedded link to the video playing
            await ctx.send("fine I'll play " + url + "... you're welcome :rolling_eyes:")
        except Exception as e:
            await ctx.send("Can't play due to exception " + str(e))

### Skipps current song in the queue and starts the recursive play again
@client.command(pass_context = True)
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(QUEUE.qsize() == 0 and not voice.is_playing()):
        await ctx.send("no song playing to skip and no songs in queue...")
    else:
        voice.stop()
        await ctx.send("yeah, that song was :peach:... Skipping...")

### really a test function to force the bot into the current channel
@client.command(pass_context = True)
async def joinVoice(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Get ya ass in a voice channel")


### leave command, also cleans up the files when it leaves
@client.command(pass_context = True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("fuck it I'm out :peace:")
        QUEUE.queue.clear()
        if(exists(PATH_TO_SONG_FILE)):
            os.remove(PATH_TO_SONG_FILE)
        if(leaveLoop.is_running() and not leaveLoop.is_being_cancelled()):
            leaveLoop.stop()
        #cleanup file if the bot leaves the channel mid song
    else:
        await ctx.send("bot not in channel")

### pause command
@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing):
        voice.pause()
    else:
        await ctx.send("no music playing")


### resume command
@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if(voice.is_paused):
        voice.resume()
    else:
        await ctx.send("no song paused")



##################### Helper Functions #####################

### checks if file exists and removes it if it does
def checkFileExists(voice):
    if exists(PATH_TO_SONG_FILE):
        if voice.is_playing():
            voice.stop()
        os.remove(PATH_TO_SONG_FILE)

### downloads the song from YT and stores it to be played
def downloadAndGetSource(voice):
    #set flag to show that the bot is currently downloading the song
    global loading_song_state
    #check if the bot is currently playing stop it and reset for next song if it is
    checkFileExists(voice)
    with youtube_dl.YoutubeDL(YDL_PROPS) as ydl:
        ydl.download([QUEUE.get()])
    for file in os.listdir(BASE_DIR_CONSTANT):
        if file.endswith(FILE_EXTENSION):
            os.rename(file, SONG_FILE)
    source = SONG_FILE
    return source

### forms the youtube query url
def getYTURL(arg):
    #multi word args come in as "blah blah" urls use "+" to concat GET request parameters
    replaceSpaces=arg.strip().replace(" ", "+")
    html = urllib.request.urlopen(YT_REQUEST_BASE_URL + replaceSpaces)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return YT_WATCH_BASE_URL + video_ids[0]

### recursive call to continue to play the queue
def playNext(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    source = downloadAndGetSource(voice)
    voice.play(FFmpegPCMAudio(source=source), after=lambda e: playAfter(ctx))

### callback function that either cleans up the file and starts the loop or plays the next song
def playAfter(ctx):
    if(QUEUE.qsize() == 0):
        if(exists(PATH_TO_SONG_FILE)):
            os.remove(PATH_TO_SONG_FILE)
        global queue_is_empty
        queue_is_empty=True
    else:
        playNext(ctx)


### once a song starts check back in every 3 minutes to see if bot needs to disconnect
@tasks.loop(minutes=3)
async def leaveLoop(voice, ctx):
    if not voice.is_playing() and not voice.is_paused() and QUEUE.qsize() == 0 and queue_is_empty:
        if(ctx.voice_client):
            if(voice.is_connected()):
                await ctx.send("fuck it I'm out :peace:")
                await ctx.guild.voice_client.disconnect()
            if(exists(PATH_TO_SONG_FILE)):
                os.remove(PATH_TO_SONG_FILE)
            leaveLoop.stop() #kill the loop until it plays a song again

client.run(APIKEY)