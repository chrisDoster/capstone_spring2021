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
import uuid
import webbrowser
import sys

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

#Sign out Link
@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

#Viewing Playlists Link
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
# Current problem with this function is that the 'token' should be retrieved from the cached file in order for the app to have
# permission to edit a user's profile. On line 102 where the 'token' is used should be 'cache_handler.get_cached_token()' but the token 
# is invalid that is retrieved is invalid and seems to break the functionality of the create playlist function.
@app.route('/create_playlist')
def create_playlist():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private', cache_handler=cache_handler, show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    token = 'BQCQl_VEaakS__RRtt_ChBkbVlOod_zNZkWScJAkwpsR39nwZievRmWupMq9VIvVFX0BICyHeU8-gKABk6ed5S1z-LWIOfnMVag5k3uBqWOHg_Aa6WKjFoV9xQEat98aMjX13Q6yBIpfbNTcOyR4X1JHbMxGRqHFKBKCddYpgvyp8as'

    #Filters for recommendations
    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    limit = 10
    market = "US"
    seed_genres = "rock"
    myPlaylist = []

    query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}'
    response = requests.get(query, headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})

    json_response = response.json()
    tracks = json_response.get('items', [])

    #Retrieving unique uri's for each recommended track
    for i, j in enumerate(json_response['tracks']):
        myPlaylist.append(j['uri'])
        print(myPlaylist[i])

    # Creating playlist for the recommended songs
    endpoint_url = f"https://api.spotify.com/v1/users/{spotify.current_user()}/playlists"
    request_body = json.dumps({
        "name": "My private playlist",
        "description": "Hopeful",
        "public": False
    })
    response = requests.post(url = endpoint_url, data = request_body, 
                            headers = {"Content-Type":"application/json", "Authorization":f"Bearer {auth_manager.get_access_token(request.args.get('code'))}"})

    print(response.status_code)
    playlist_id = json_response.get('id', [])
    print(str(playlist_id))
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    request_body = json.dumps({
    "myPlaylist" : myPlaylist
    })

    # url = resp.get('external_urls','spotify')
    # print(response.status_code)
    #playlist_name = "Random playlist"
    #playlist_id = ''
    #playlist = spotify.user_playlist_create(spotify.current_user(), name=playlist_name, public=False)
    # for playlist in playlists['items']:
    #     if playlist['name'] == playlist_name:
    #         playlist_id = playlist['id']

    # Filling new playlist with recommended songs
    # if playlist_id is None:
    #     print('99999999999')
    # else:
    #     print(playlist_id)
    # endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    # request_body = json.dumps({
    #     "myPlaylist" : myPlaylist
    # })

    #Getting id for each song
    song_id_list = []

    for i, j in enumerate(json_response.get('tracks', [])):
        track_id = spotify.search(q='artist:' + j['artists'][0]['name'] + ' track:' + j['name'], type='track')
        items = track_id['tracks']['items']
        trackid = ''
        if len(items) > 0:
            trackid = items[0]
        else:
            print('000000000000000000000000000000000000')   #Testing if there are any items
        song_id_list.append(trackid['id'])
        print(song_id_list[i])

    #Adding each song to the created playlist
    for i in song_id_list:
        song = [i]
        spotify.user_playlist_add_tracks(spotify.current_user(), playlist_id, song)

    song_id_list.clear()

    webbrowser.open("https://open.spotify.com/")
    return 'OK'

if __name__ == '__main__':
    app.run()