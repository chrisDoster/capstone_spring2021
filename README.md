# capstone_spring2021

Summary
   BerndBeats is an application to provide Spotify recommendations based on Twitter activity. When run, the application will:
 - read Tweets from a user (using tweepy)
 - assign an emotional value to these Tweets (using emotionPredictor)
 - use these emotional values to calculate filter values for Spotify
 - retrieve 10 songs from Spotify (using spotipy) with up to 5 randomly chosen genres
 - create a playlist for a user’s account on Spotify

.spotify_caches (folder): This is not found within the GitHub repository but is created when the flask session is run which holds the cache file with access tokens to grant Spotify authorization.

main.py: Starts and runs the flask session and retrieves the tokens required to modify Spotify accounts.
Methods include:
  *Index(): For creating the initial web page and retrieving the access tokens for Spotify authorization.
  
  *Sign_out(): For signing out of the application.
  *Create_playlist(useAF=False): Takes a parameter that determines whether to use the audio features(AF) given from the analysis algorithm or to use default filters.       This function will then use Spotify to create a list of 10 recommended songs based on the default filters or the given filters from tweet analysis. It then uses the access tokens to make the playlist on Spotify and fill it with the list of songs created before. Finally it returns an HTML string that will return a formatted web page with the username, sign-out link, create playlist link, the list of recommended songs, and then a link that will redirect to the created playlist in Spotify.
  *AudioFeaturesQuery(audiofeatures): Returns a string containing a formatted query to get recommendations from Spotify 
  *PullTweets(): Uses tweepy to retrieve Tweets from Twitter

Emotion_predictor.py: Part of EmotionPredictor dependency - Dependency used to get emotional breakdown on Tweets.

Moodstate.py: Wrapper class for a dictionary of emotions and the number of occurrences of these emotions in a set of Tweets

Tweetparser.py: Simple utility class to clean the formatting of Tweets pulled from Twitter, this consists primarily of removing links from Retweets and Tweets that have media

Userprofile.py: Stores data about a user’s preferences in music

Models (folder): Part of EmotionPredictor dependency

Postman test.txt: Text file of the test script to put in Postman to test running application (main.py).

Postman_API_test.json: JSON file uploaded from Postman to Github repository.
