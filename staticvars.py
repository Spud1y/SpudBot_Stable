APIKEY="YOUR API KEY HERE"
YDL_PROPS={
            'format': 'bestaudio/best',       
            'postprocessors':[{
                'key': "FFmpegExtractAudio",
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
COMMAND_LIST="""**__COMMAND LIST__**
*prefix is '!' `!commands` shows this list and anything wrapped in <> is an argument i.e. !play <song-name> would translate to '!play never gonna give you up'*\n
1. **!play <song-name>** --song-name can be multi word name that will search youtube or a youtube video link. Will add song to end of queue if song is playing
2. **!skip** -- skips the current song playing and goes to the next one in the queue
3. **!leave** -- bot leaves the channel and the queue is emptied
4. **!pause** -- pauses the current song
5. **!resume** -- resumes the current paused song
6. **!queue** -- lists current queue of songs
7. **!emptyQueue** -- empties all songs in the queue, does not stop playing current song
8. **!playlists** -- lists names of current playlists
9. **!playPlaylist <playlist-name>** -- adds all songs in the playlist to the queue
10. **!createPlaylist <playlist-name>** -- creates a new playlist with the given name (must be 1 word playlists)
11. **!deletePlaylist <playlist-name>** -- deletes playlist with the given name
12. **!showPlaylist <playlist-name>** -- prints list of songs in the playlist
13. **!addSong <playlist-name> <song-name>** -- adds <song-name> to the given playlist (song can be multi word)
14. **!deleteSong <playlist-name> <song-number>** -- removes song from playlist. Must first list the playlist where <song-number> is the number next to the song in the playlist
15. **!importPlaylist <playlist-name> <youtube-url-link-to-playlist>** -- get all songs in a youtube playlist and adds them to the desired playlist **IMPORTANT PLAYLIST MUST BE PUBLIC OR UNLISTED TO PULL**"""