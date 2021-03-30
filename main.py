# Twitter Dependencies
import tweepy
# Spotify Dependencies
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import argparse
import logging
import requests
import json

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
spotify_client_id = '7955beeac6734d048ebd62498bb8cd05'
spotify_client_secret = '96a99012fd0843d39434188e6356fbc6'
spotify_client_redirect_uri = 'http://localhost:3000'
user_id = "1263578962"
scope = 'playlist-modify-private'
token = util.prompt_for_user_token(user_id, scope, spotify_client_id, spotify_client_secret, spotify_client_redirect_uri)
spo = spotipy.Spotify(auth = token)
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))

uri = 'spotify:artist:2yEwvVSSSUkcLeSTNyHKh8'
results = spotify.artist_top_tracks(uri)

for track in results['tracks'][:10]:
    print('Track:   ' + track['name'])
    print('Album:   ' + track['album']['name'])
    print('Artist:  ' + track['artists'][0]['name'])
    print('Audio Sample: ' + track['preview_url'])
    print()

# SPOTIFY
# Creating recommended playlist
endpoint_url = "https://api.spotify.com/v1/recommendations?"
limit = 10
market = "US"
seed_genres = "rock"
myPlaylist = []

query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}'
response = requests.get(query, headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})

json_response = response.json()
for i in json_response['tracks']:
    myPlaylist.append(i)
    print(f"\"{i['name']}\" by {i['artists'][0]['name']}")

# Creating playlist of recommended songs on spotify account
endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
request_body = json.dumps({
    "name": "My private playlist",
    "description": "Hopeful",
    "public": False
})
response = requests.post(url = endpoint_url, data = request_body, 
                        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"})

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
    spo.user_playlist_add_tracks(user_id, playlist_id, tracks = [j])

song_id_list.clear()
