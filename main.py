# Twitter Dependencies
import tweepy
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
           f'<a href="/create_playlists">create new playlists</a> | ' \
            f'<a href="/current_user">me</a>' \

@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


# TWITTER
# for cnd243@twitter.com (chris) ; NOTE: I only follow 1 person atm, an author named Ursula K Le Guin
twitter_api_key = "eu0hXaGudKMlb93aAlIbJBYF1"
twitter_api_key_secret = "tywK4Vzses8Pt0GprxWUuDQJ0G3aRKARmBN1cXdO2Kp3r9syTn"
twitter_access_token = "1364394392577056773-HD04xN1RPm8g9uE5jRU5RTZS2kA3w7"
twitter_access_token_secret = "VLbcymTCK8RkvpCdsCwZCyADthXtbbhSClZw6zmnGPVtZ"

# authenticate to twitter
auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tl = api.home_timeline()
for tweet in tl:
    print(f"{tweet.user.name} said: {tweet.text}")


# SPOTIFY
# for BerndBeats on Spotify
# spotify_client_id = '7595beeac6734d048ebd62498bb8cd05'
# spotify_client_secret = '96a99012fd0843d39434188e6356fbc6'
# spotify_client_redirect_uri = 'http://localhost:8080'
# user_id = "1263578962"
# scope = 'playlist-modify-private'
# token = util.prompt_for_user_token(user_id, scope, spotify_client_id, spotify_client_secret, spotify_client_redirect_uri)
# spo = spotipy.Spotify(auth = token)
# spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))

# SPOTIFY
# Creating recommended playlist
def create_playlist():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    limit = 10
    market = "US"
    seed_genres = "rock"
    myPlaylist = []

    query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}'
    response = requests.get(query, headers = {"Content-Type":"application/json", "Authorization":f"Bearer {spotify.get_access_token()}"})

    json_response = response.json()
    for i in json_response['tracks']:
        myPlaylist.append(i)
        return(f'<h2>{i.name}</h2>')

        return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/create_playlists">create new playlists</a> | ' \
            f'<a href="/current_user">me</a>' \
        #print(f"\"{i['name']}\" by {i['artists'][0]['name']}")

    # Creating playlist of recommended songs on spotify account
    endpoint_url = f"https://api.spotify.com/v1/users/{spotify.current_user()}/playlists"
    request_body = json.dumps({
        "name": "My private playlist",
        "description": "Hopeful",
        "public": False
    })
    response = requests.post(url = endpoint_url, data = request_body, 
                            headers = {"Content-Type":"application/json", "Authorization":f"Bearer {spotify.get_access_token()}"})

    url = response.json()['external_urls']['spotify']
    print(response.status_code)

    # Filling new playlist with recommended songs
    playlist_id = response.json()['id']
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    request_body = json.dumps({
        "myPlaylist" : myPlaylist
    })

    print(response.status_code)
    print(f'Playlist can be found at {url}')

    song_id_list = []

    for i in json_response['tracks']:
        track_id = spotify.search(q='artist:' + i['artists'][0]['name'] + ' track:' + i['name'], type='track')
        items = track_id['tracks']['items']
        if len(items) > 0:
            trackid = items[0]
        song_id_list.append(trackid['id'])

    for j in song_id_list:
        spotify.current_user().user_playlist_add_tracks(index().current_user(), playlist_id, tracks = [j])

    song_id_list.clear()

if __name__ == '__main__':
    app.run()