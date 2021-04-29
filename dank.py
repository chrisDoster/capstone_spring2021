# Spotify Dependencies
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
# Token Dependencies
import os
from flask import Flask, session, request, redirect
from flask_session import Session
# Other Dependencies
import uuid
import webbrowser
import sys
import logging
import shutil

# Token System
os.environ['SPOTIPY_CLIENT_ID'] = '7955beeac6734d048ebd62498bb8cd05'
os.environ['SPOTIPY_CLIENT_SECRET'] = '96a99012fd0843d39434188e6356fbc6'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:5000/'
os.environ['FLASK_ENV'] = 'development'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session'
Session(app)

caches_folder = './.spotify_caches/'

if os.path.exists(caches_folder):
    shutil.rmtree(caches_folder)

if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private', cache_handler=cache_handler, show_dialog=True)

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        print(auth_manager.get_access_token(request.args.get("code")))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/create_playlist">create new playlists</a> | ' \
            f'<a href="/current_user">me</a>' \

# Sign out Link
@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

# Viewing Playlists Link
@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return 'OK'

# SPOTIFY
# Creating recommended playlist
@app.route('/create_playlist')
def create_playlist():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private', cache_handler=cache_handler, show_dialog=True)

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    #token = 'BQD0Q-5PbTr-nMpQ-Y2ODcKKxl7ATarvBAH0Ny8B3lY_BN_gx82uFfpl9iDCAsO1DqYq9Yj6_1NxVWHT6vkCHXSMdsEPavHPHijqskqd6hGu8tGXuzNuC1TzjNuep9BT22KK6JeAiNv4I09192t44z-MPXWISPwxgMPtF-rsZbBVQAo'
    user_id = '1263578962'

    # Used to find user token & user ID
    cached_file_string = str(cache_handler.get_cached_token())
    token = cached_file_string[18:196]
    user_string = str(spotify.current_user())
    index_one = user_string.find("'id':")
    index_two = user_string.find("'images':")
    user_id = user_string[index_one+7:index_two-3]
    print(user_id)

    # Filters for recommendations
    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    limit = 10
    market = "US"
    seed_genres = "rock"
    myPlaylist = []

    query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}'
    response = requests.get(query, headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})

    json_response = response.json()
    tracks = json_response.get('items', [])
    print(tracks)

    # Retrieving unique uri's for each recommended track
    for i, j in enumerate(json_response['tracks']):
        myPlaylist.append(j['uri'])
        print(myPlaylist[i])

    # Creating playlist for the recommended songs
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    request_body = json.dumps({
        "name": "My private playlist",
        "description": "Hopeful",
        "public": False
    })
    response = requests.post(url = endpoint_url, data = request_body, 
                            headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})

    print(response.status_code)
    playlist_id = response.json()['id']
    print(str(playlist_id))
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    request_body = json.dumps({
    "myPlaylist" : myPlaylist
    })

    print(response.status_code)

    # Filling new playlist with recommended songs
    if playlist_id is None:
        print('99999999999')
    else:
        print(playlist_id)
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    request_body = json.dumps({
        "myPlaylist" : myPlaylist
    })

    # Getting id for each song
    song_id_list = []

    for j in json_response['tracks']:
        track_id = spotify.search(q='artist:' + j['artists'][0]['name'] + ' track:' + j['name'], type='track')
        items = track_id['tracks']['items']
        trackid = ''
        if len(items) > 0:
            trackid = items[0]
        else:
            print('000000000000000000000000000000000000')   #Testing if there are any items
        song_id_list.append(trackid['id'])
        #print(song_id_list[j])

    # #Adding each song to the created playlist
    for i in song_id_list:
        spotify.user_playlist_add_tracks(spotify.current_user(), playlist_id, tracks= [i])

    song_id_list.clear()

    webbrowser.open(f"https://open.spotify.com/playlist/{playlist_id}")
    return 'OK'

if __name__ == '__main__':
    app.run()