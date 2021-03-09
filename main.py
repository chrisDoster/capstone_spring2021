import tweepy

# for cnd243@twitter.com (chris) ; NOTE: I only follow 1 person atm, an author named Ursula K Le Guin
api_key = "eu0hXaGudKMlb93aAlIbJBYF1"
api_key_secret = "tywK4Vzses8Pt0GprxWUuDQJ0G3aRKARmBN1cXdO2Kp3r9syTn"
access_token = "1364394392577056773-HD04xN1RPm8g9uE5jRU5RTZS2kA3w7"
access_token_secret = "VLbcymTCK8RkvpCdsCwZCyADthXtbbhSClZw6zmnGPVtZ"

# authenticate to twitter
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tl = api.home_timeline()
for tweet in tl:
    print(f"{tweet.user.name} said: {tweet.text}")