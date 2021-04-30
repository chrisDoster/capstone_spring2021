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
# Other Dependencies
import uuid
import webbrowser
import sys
import logging
import shutil
# Internal Dependencies
import moodstate
import tweetparser
import userprofile

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
    searchWithAF = False

    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private', cache_handler=cache_handler, show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        print(auth_manager.get_access_token(request.args.get("code")))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return f'<body style="background-color:orange;">' \
           f'<h1><center><br><br><br><br><br><br>Welcome to BerndBeats!</center></h1>' \
           f'<h2><center><a href="{auth_url}">Sign in</a></center></h2>' \

    return f'<body style="background-color:orange;"><br><br><br><br>' \
           f'<h1><center>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></center></h1>' \
           f'<h1><center><a href="/create_playlist/{searchWithAF}">Create New Playlist</a></center></h1>' \

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
@app.route('/create_playlist/<useAF>')
def create_playlist(useAF=False):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private', cache_handler=cache_handler, show_dialog=True)

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # Used to parse user token from cached file
    cached_file_string = str(cache_handler.get_cached_token())
    index_one = 18
    index_two = cached_file_string.find("'token_type':")
    token = cached_file_string[index_one:index_two-3]

    # Used to parse user id from spotify.current_user() output
    user_string = str(spotify.current_user())
    index_one = user_string.find("'id':")
    index_two = user_string.find("'images':")
    user_id = user_string[index_one+7:index_two-3]

    print(user_id)
    print(cache_handler.get_cached_token())
    print(token)
    print(spotify.current_user())

    # Filters for recommendations
    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    limit = 10
    market = "US"
    seed_genres = "rock"
    myPlaylist = []
    
    target_danceability=0.9

    query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}&target_dancability={target_danceability}'
    # algorithm code, commented for performance while testing
    """if useAF:# find search criteria by mood
        user = userprofile.UserProfile()
        tweets = pullTweets()
        mood = moodstate.MoodState.createState(tweets)
        searchCriteria = user.audioFeatureValues(mood)
        seed_genres = user.pickSeedGenres()
        query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}'
        query += audioFeaturesQuery(searchCriteria)"""
    print(f'///QUERY///{query}///QUERY///')
    response = requests.get(query, headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})
    print(f'///RESPONSE///{response.json()}///RESPONSE///')

    json_response = response.json()
    tracks = json_response.get('items', [])

    # Retrieving unique uri's for each recommended track
    string = ''
    for i, j in enumerate(json_response['tracks']):
        myPlaylist.append(j['uri'])
        string += j['name'] + ' by ' + j['artists'][0]['name'] + '<br><br>'
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
            song_id_list.append(trackid['id'])
        else:
            create_playlist()

    # #Adding each song to the created playlist
    for i in song_id_list:
        spotify.user_playlist_add_tracks(spotify.current_user(), playlist_id, tracks= [i])

    song_id_list.clear()

    #webbrowser.open(f"https://open.spotify.com/playlist/{playlist_id}")
    print(string)
    return f'<body style="background-color:orange;"><br><br><br><br>' \
           f'<h1><center>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></center></h1>' \
           f'<h1><center><a href="/create_playlist/{useAF}">Create New Playlist</a></center></h1>' \
           f'<center><p>{string}</p></center>' \




# builds and returns a string representing a standard Spotify query, including the target values of each audiofeature that is passed as a parameter
# @param audiofeatures: a dict containing the target values for various audio features
def audioFeaturesQuery(audiofeatures): #fixme: create query for searching by audio feature and return as string
    target_dancability = audiofeatures['dancability']
    target_energy = audiofeatures['energy']
    target_loudness = audiofeatures['loudness']
    target_mode = audiofeatures['mode']
    target_accousticness = audiofeatures['accousticness']
    target_instrumentalness = audiofeatures['instrumentalness']
    target_valence = audiofeatures['valence']
    query = f'&target_dancability={target_dancability}&target_energy={target_energy}'
    query += f'&target_loudness={target_loudness}&target_mode={target_mode}&target_accousticness={target_accousticness}'
    query += f'&target_instrumentalness={target_instrumentalness}&target_valence={target_valence}'
    return query




def pullTweets():
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

    userID = 'cnd243'
    tl = api.user_timeline(screen_name=userID, include_rts=False, tweet_mode='extended')
    parser = tweetparser.TweetParser()
    cleaned = []
    for tweet in tl:
        cleaned.append(parser.clean(tweet.full_text))
    return cleaned

if __name__ == '__main__':
    app.run()