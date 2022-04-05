import discord
import os
import queue
import re
import time
import urllib.request
from numpy import true_divide
import youtube_dl
import asyncio
import io

from discord.ext import commands, tasks
from discord.player import FFmpegPCMAudio
from pytube import Playlist
from os.path import exists
from staticvars import APIKEY
from staticvars import YDL_PROPS
from staticvars import COMMAND_LIST

#File constants
OS_SEPARATOR= os.path.sep #ensures file separator is correct if using linux shell
BASE_DIR_CONSTANT="." + OS_SEPARATOR
PLAYLIST_DIR=BASE_DIR_CONSTANT + "playlists"

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
    if(exists(PLAYLIST_DIR)):
        print('playlist repo already exists skipping creation')
    else:
        print('playlist repo does not exist, creating')
        os.makedirs(PLAYLIST_DIR)



################ COMMANDS ##################

@client.command(pass_context = True)
async def commands(ctx):
    await ctx.send(COMMAND_LIST)

### Main play command that pulls bot into channel and plays song also starts the recursive queue playing
@client.command(pass_context = True)
async def play(ctx, *, arg):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice and ctx.message.author.voice.channel != voice.channel):
        print("can't play songs while user is not in same channel as bot")
        return
    #url = getYTURL(arg)
    songTitle = "".join(arg)
    #if a song is playing or queue is already filled up, add to the back of queue
    if voice != None and (QUEUE.qsize() >= 1 or voice.is_playing()):
        await ctx.send("added: `" + songTitle + "` to the queue")
    QUEUE.put(songTitle)
    global queue_is_empty
    queue_is_empty=False

    if(voice == None or not voice.is_playing()):
        try:
            #check if bot is in current channel, move it if needed
            if(ctx.author.voice):
                channel = ctx.message.author.voice.channel
                if(voice == None):
                    voice = await channel.connect()
            await playNext(ctx)

            #give user feedback with embedded link to the video playing
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
        QUEUE.queue.clear()
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
        await ctx.guild.voice_client.disconnect()
        await ctx.send("fuck it I'm out :peace:")
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


########## Playlist commands #############
@client.command(pass_context = True)
async def playlists(ctx):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(PLAYLIST_DIR)]
    playlistDirList = '\n'.join(files)
    await ctx.send('list of playlists are:\n>>> {}'.format(playlistDirList))

@client.command(pass_context = True)
async def createPlaylist(ctx, *arg):
    if(len(arg) > 1):
        await ctx.send("Playlist length connot be more than 1 word")
    else:
        newPlaylistName = arg[0]
        newPlaylistFile = getPlaylistfile(newPlaylistName)
        if(exists(newPlaylistFile)):
            await ctx.send("playlist by name " + newPlaylistName + " already exists")
        else:
            await ctx.send("creating playlist " + arg[0])
            with io.open (newPlaylistFile, "w", encoding="utf-8") as f:
                f.close()

@client.command(pass_context = True)
async def deletePlaylist(ctx, *arg):
    if(len(arg) != 1):
        await ctx.send("Playlist length connot be more than 1 word")
    else:
        deletePlaylistName = arg[0]
        deletePlaylistFile = getPlaylistfile(deletePlaylistName)
        if(exists(deletePlaylistFile)):
            os.remove(deletePlaylistFile)
            await ctx.send("Playlist " + deletePlaylistName + " deleted")
        else:
            await ctx.send("playlist by name " + deletePlaylistName + " does not exists")


@client.command(pass_context = True)
async def showPlaylist(ctx, *arg):
    if(len(arg) != 1):
        await ctx.send("Invalid number of arguments can only list 1 playlist at a time")
    else:
        requestedPlaylist = arg[0]
        requestedPlaylistFile = getPlaylistfile(requestedPlaylist)
        if(exists(requestedPlaylistFile)):
            lines = ""
            songList = []
            with io.open (requestedPlaylistFile, "r", encoding="utf-8") as f:
                lines = f.readlines()
                count = 1
                for line in lines:
                    songList.append('{}. {}'.format(count,line))
                    count+=1
                f.close()
            listOfSongLists = []
            if(len(songList) > 25):
                listOfSongLists = [songList[i:i + 25] for i in range(0, len(songList), 25)]
            else:
                listOfSongLists.append(songList)
            await ctx.send('**Songs in playlist: __{}__**'.format(requestedPlaylist))
            for subLists in listOfSongLists:
                await ctx.send("```{}```".format("".join(subLists)))
        else:
            await ctx.send("no playlist found with name {}".format(requestedPlaylist))

@client.command(pass_context = True)
async def addSong(ctx, *arg):
    if(len(arg) < 2):
        await ctx.send("need at least 2 arguments")
    else:
        argList = list(arg)
        playlistName = argList.pop(0)
        song = " ".join(argList)
        playlistFile = getPlaylistfile(playlistName)
        if(exists(playlistFile)):
            with io.open (playlistFile, "a", encoding="utf-8") as f:
                f.writelines(song + "\n")
                f.close()
            await ctx.send("song `{}` was added to the playlist {}".format(song, playlistName))
        else:
            await ctx.send("no playlist found with name {}".format(playlistName))

@client.command(pass_context = True)
async def deleteSong(ctx, *arg):
    if(len(arg) != 2):
        await ctx.send("invalid number of arguments need 2")
    else:
        indexNumber = arg[1]
        try:
            indexInt = int(indexNumber)
            playlistName = arg[0]
            playlistFile = getPlaylistfile(playlistName)
            if(exists(playlistFile)):
                lines = ""
                with io.open (playlistFile, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    f.close()
                if(len(lines) < indexInt):
                    await ctx.send("invalid number must be less than or equal to {}".format(len(lines)))
                else:
                    deletedSong = lines.pop(indexInt-1)
                    with io.open (playlistFile, "w", encoding="utf-8") as f:
                        for song in lines:
                            f.writelines([song])
                        f.close()
                    await ctx.send("song `{}` was removed from the playlist".format(deletedSong))
        except ValueError:
            await ctx.send("Second argument {} must be a number but is {}".format(indexNumber, type(indexNumber)))

@client.command(pass_context = True)
async def importPlaylist(ctx, *args):
    if(len(args) > 2):
        await ctx.send("invalid number of inputs")
    else:
        playlist = args[0]
        playlistFile = getPlaylistfile(playlist)
        ytPlayList = Playlist(args[1])
        ytPlayListLength = len(ytPlayList.videos)
        await ctx.send("adding {} songs to playlist `{}` one moment... ".format(ytPlayListLength, playlist))
        songs = []
        for video in ytPlayList.videos:
            songs.append(video.title)
        print("writing {} lines to new playlist {}".format(ytPlayListLength, playlist))
        with io.open (playlistFile, "a", encoding="utf-8") as f:
            for song in songs:
                f.writelines(song + "\n")
            f.close()
        print("done writing {} lines to new playlist {}".format(ytPlayListLength, playlist))
        await ctx.send ("all {} songs have been added to playlist `{}`".format(ytPlayListLength, playlist))

@client.command(pass_context = True)
async def playPlaylist(ctx, *args):
    if(len(args) != 1):
        await ctx.send("invalid number of arguments")
    else:
        playlist = args[0]
        playlistFile = getPlaylistfile(playlist)
        if(exists(playlistFile)):
            lines = ""
            with io.open (playlistFile, "r", encoding="utf-8") as f:
                lines = f.readlines()
                f.close()
            for song in lines:
                #url = getYTURL(song)
                songTitle = "".join(song)
                QUEUE.put(songTitle)
            await ctx.send("songs from playlist `{}` added to queue".format(playlist))
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            if(voice == None or not voice.is_playing()):
                try:
                    #check if bot is in current channel, move it if needed
                    if(ctx.author.voice):
                        channel = ctx.message.author.voice.channel
                        if(voice == None):
                            voice = await channel.connect()
                    await playNext(ctx)
                    #give user feedback with embedded link to the video playing
                    await ctx.send("all {} songs from playlist `{}` were added to queue".format(len(lines), playlist))
                except Exception as e:
                    await ctx.send("Can't play due to exception " + str(e))
        else:
            await ctx.send("could not find playlist `{}`".format(playlist))

@client.command(pass_context = True)
async def queue(ctx):
    listOfSongLists = []
    if(QUEUE.qsize() == 0):
        await ctx.send("Current queue is empty")
    else:
        qList = []
        for n in list(QUEUE.queue):
            qList.append(n)

        if(len(qList) > 25):
            listOfSongLists = [qList[i:i + 25] for i in range(0, len(qList), 25)]
        else:
            listOfSongLists.append(qList)
        await ctx.send("**__current queue:__**")
        for subLists in listOfSongLists:
            await ctx.send("```{}```".format("".join(subLists)))

@client.command(pass_context = True)
async def emptyQueue(ctx):
    if(QUEUE.qsize() == 0):
        await ctx.send("Current queue is empty")
    else:
        QUEUE.queue.clear()
        await ctx.send("queue has been cleared")

##################### Helper Functions #####################

def getPlaylistfile(arg):
    return PLAYLIST_DIR + OS_SEPARATOR + arg + ".txt"

### forms the youtube query url
def getYTURL(arg):
    #multi word args come in as "blah blah" urls use "+" to concat GET request parameters
    if arg.startswith('http') or arg.startswith('https'): 
        return arg
    regexReplace = re.sub('[^A-Za-z0-9]+', ' ', arg)
    replaceSpaces = regexReplace.strip().replace(" ", "+")
    html = urllib.request.urlopen(YT_REQUEST_BASE_URL + replaceSpaces)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return YT_WATCH_BASE_URL + video_ids[0]

### recursive call to continue to play the queue
async def playNext(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format':"bestaudio"}
    vc = ctx.voice_client

    url = getYTURL(QUEUE.get())
    await ctx.send(":potato: :guitar: Next up to play " + url)
    os.system("youtube-dl --rm-cache-dir")
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source, after = lambda e: asyncio.run_coroutine_threadsafe(playAfter(ctx, vc), client.loop))


### callback function that either cleans up the file and starts the loop or plays the next song
async def playAfter(ctx, vc):
    if(QUEUE.qsize() == 0):
        await vc.disconnect()
    else:
        await playNext(ctx)


### once a song starts check back in every 3 minutes to see if bot needs to disconnect
#@tasks.loop(minutes=10)
#async def leaveLoop(voice, ctx):
#    if not voice.is_playing() and not voice.is_paused() and QUEUE.qsize() == 0 and queue_is_empty:
#        if(ctx.voice_client):
#            if(voice.is_connected()):
#                await ctx.send("fuck it I'm out :peace:")
#                await ctx.guild.voice_client.disconnect()
#            if(exists(PATH_TO_SONG_FILE)):
#                os.remove(PATH_TO_SONG_FILE)
#            leaveLoop.stop() #kill the loop until it plays a song again

client.run(APIKEY)