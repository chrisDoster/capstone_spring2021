import re

class TweetParser:

    def _cleanTweet(self, tweet):
        cleaned = ''
        tokenizedTweet = tweet.split(' ')
        for token in tokenizedTweet:
            urlPos1 = token.find('https:')
            urlPos2 = token.find('http:')
            hashtagPos = token.find('#')
            if urlPos1==-1 and urlPos2==-1 and hashtagPos==-1:
                cleaned += token + ' '
        
        return cleaned

    def _cleanList(self, tweets):
        cleaned = []
        for t in tweets:
            cleaned.append(self._cleanTweet(t))
        
        return cleaned

    # removes urls and hashtags from a tweet or list of tweets passed as a parameter
    def clean(self, tweet):
        cleaned = '<unset>'
        if type(tweet) is list:
            cleaned = self._cleanList(tweet)
        if isinstance(tweet, str):
            cleaned = self._cleanTweet(tweet)
        return cleaned