from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import base64
from urllib.parse import urlencode
import webbrowser
import os
import requests
import config
import time
paused = 0
client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET
mute = False

webbrowser.open_new('file://' + os.path.realpath('file:///C:/Users/ypawa/OneDrive/Documents/GitHub/Spotify-Ad-Blocker/lyrics.html'))
f = open("lyrics.html", "w")

def mute_windows():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = cast(session._ctl.QueryInterface(ISimpleAudioVolume), POINTER(ISimpleAudioVolume))
        volume.SetMute(True, None)

def unmute_windows():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = cast(session._ctl.QueryInterface(ISimpleAudioVolume), POINTER(ISimpleAudioVolume))
        volume.SetMute(False, None)

auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "http://localhost:7777/callback",
    "scope": "user-read-playback-state"
}
webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))
code = input("Enter code: ")

##ENTER THE URL LINK. DONT INCLUDE THE PART BEFORE 'code='

encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")

token_headers = {
    "Authorization": "Basic " + encoded_credentials,
    "Content-Type": "application/x-www-form-urlencoded"
}

token_data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "http://localhost:7777/callback"
}

r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
token = r.json()["access_token"]
user_headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}
print('program started')

song_name = ''
while True:
    if (paused > 40):
        break
    playback_response = requests.get('https://api.spotify.com/v1/me/player', headers=user_headers)
    playback_response = playback_response.json()
    current_song_name = playback_response["item"]["name"]
    
    #if song detected on last api api call is not same as song detected on current api call:
    #call lyrics
    #update lyrics html
    if (song_name != current_song_name):
        artist_name = playback_response["item"]["artists"][0]["name"]
        lyrics_api_call = 'https://api.lyrics.ovh/v1/' + artist_name + '/' + current_song_name
        try: 
            r = requests.get(lyrics_api_call)
            lyrics = r.json()['lyrics']
            lyrics = lyrics.replace('\r\n', '<br>')
            lyrics = lyrics.replace('\n', '<br>')
            
            f = open("lyrics.html", "w")
            f.write("<html><head><title>song lyrics</title></head><body><h1>Start listening and reload page to find your song lyrics</h1><br>"+lyrics+"</body></html>")
        except: 
            print("no lyrics")    
            f = open("lyrics.html", "w")
            f.write("<html><head><title>song lyrics</title></head><body><h1>No Lyrics Available</h1><br>Lyrics not found for this song</body></html>")

        f.close()
        
    song_name = current_song_name    
    if 'pausing' in (playback_response["actions"]['disallows']):
        paused += 1
    if (playback_response["currently_playing_type"]) == 'ad':
        print('MUTED SOUND! AD!')
        if mute == False:
            mute_windows()
            mute = True
    else: 
        if mute == True:
            unmute_windows()
            mute = False
    time.sleep(3)
unmute_windows()
print('PROGRAM ENDED')

