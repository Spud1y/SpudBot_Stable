# SpudBot

How to run (Windows):

- Install latest python version
- run "py -3 -m pip install -U discord.py[voice]" to install discord library
- run "py -3 -m pip install -U youtube_dl"
- Next you need to download ffmpeg -- this is the library to actually play the audio files
  1. go to https://ffmpeg.org/ and navigate to download
  2. go to "Windows builds by BtbN"
  3. download ffmpeg-n4.4-152-gdf288deb9b-win64-gpl-4.4.zip
     - note that the version may be different... i.e. ffmpeg-n4.5-191-gdf288deb9b-win64-gpl-5.5.zip point is grab the win64-gpl zip
  4. uzip the file and create a new folder somewhere in your C drive (or whever you want to run but SSD is reccommended for speed)
  5. take the 3 files from the unzipped ffmpeg file and paste it into your newly created folder from step 4
- Next we need to install ffmpeg

  1. in windows search type "Environment Variables" and click the "Edit System Environment variables"
  2. click on "Environment Variables..." in the bottom right of the window that pops up
  3. in the "System Variables" section, find the "Path" variable highlight it and click edit
  4. Click "new" on the right side
  5. Copy the path the folder created in the download ffmpeg step in here

  - example if you put your file in your C drive and named it ffmpeg then the path would be "C:\ffmpeg"

  6. click ok>ok to get out of the menus
  7. verify it's installed by opening a comand prompt (search for "cmd")
  8. type "ffmpeg --version"
  9. this should give a version of ffmpeg

- Now take this code replace the APIKey with your API key for your music bot
- Add the bot to your server
- run this script by navigating to the repo and typing "py bot.py" to run the script
- Enjoy
