from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import base64
from urllib.parse import urlencode
import webbrowser
import requests
import config
import time
paused = 0
client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET
mute = False
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

while True:
    if (paused > 40):
        break
    playback_response = requests.get('https://api.spotify.com/v1/me/player', headers=user_headers)
    playback_response = playback_response.json()
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
    time.sleep(2)
unmute_windows()

