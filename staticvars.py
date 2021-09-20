APIKEY="YOUR API KEY HERE"
YDL_PROPS={
            'format': 'bestaudio/best',       
            'postprocessors':[{
                'key': "FFmpegExtractAudio",
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }