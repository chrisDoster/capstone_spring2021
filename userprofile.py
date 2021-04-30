import moodstate
import statistics
import copy

class UserProfile:
    def __init__(self):
        self.__preference = {'Joy' : {'dancability':1.0, 'energy':.6, 'loudness':.6, 'mode':1, 'accousticness':.5, 'instrumentalness':.5, 'valence':1.0},
                             'Anger' : {'dancability':.8, 'energy':1.0, 'loudness':.8, 'mode':1, 'accousticness':.5, 'instrumentalness':.5, 'valence':.2},
                             'Disgust' : {'dancability':.5, 'energy':.5, 'loudness':.5, 'mode':1, 'accousticness':.5, 'instrumentalness':.5, 'valence':.6},
                             'Sadness' : {'dancability':.5, 'energy':.5, 'loudness':.2, 'mode':0, 'accousticness':.5, 'instrumentalness':.5, 'valence':.1},
                             'Surprise' : {'dancability':.6, 'energy':.6, 'loudness':.5, 'mode':0, 'accousticness':.5, 'instrumentalness':.5, 'valence':.5},
                             'Fear' : {'dancability':.5, 'energy':.6, 'loudness':.1, 'mode':0, 'accousticness':.5, 'instrumentalness':.5, 'valence':.5}}
    
    # helper to build a string representing the column-labels for the preferenceStr method
    def _labelStr(self, pad, leadPad):
        label = 'PREFERENCE'.ljust(leadPad, ' ')
        label += 'dancability'.rjust(pad, ' ')
        label += 'energy'.rjust(pad, ' ')
        label += 'loudness'.rjust(pad, ' ')
        label += 'mode'.rjust(pad, ' ')
        label += 'accousticness'.rjust(pad, ' ')
        label += 'instrumentalness'.rjust(pad, ' ')
        label += 'valence'.rjust(pad, ' ')
        label += '\n'
        return label

    # helper to build string representing a single row for the preferenceStr method
    def _rowStr(self, emo, pad, leadPad):
        row = emo.ljust(leadPad, ' ')
        row += str(self.__preference[emo]['dancability']).rjust(pad, ' ')
        row += str(self.__preference[emo]['energy']).rjust(pad, ' ')
        row += str(self.__preference[emo]['loudness']).rjust(pad, ' ')
        row += str(self.__preference[emo]['mode']).rjust(pad, ' ')
        row += str(self.__preference[emo]['accousticness']).rjust(pad, ' ')
        row += str(self.__preference[emo]['instrumentalness']).rjust(pad, ' ')
        row += str(self.__preference[emo]['valence']).rjust(pad, ' ')
        row += '\n'
        return row

    # returns a string representation of a table of preference values from the __preference field
    def preferenceStr(self):
        leadPad = 11
        pad = 17
        prefStr = self._labelStr(pad, leadPad)
        prefStr += self._rowStr('Joy', pad, leadPad)
        prefStr += self._rowStr('Anger', pad, leadPad)
        prefStr += self._rowStr('Disgust', pad, leadPad)
        prefStr += self._rowStr('Sadness', pad, leadPad)
        prefStr += self._rowStr('Surprise', pad, leadPad)
        prefStr += self._rowStr('Fear', pad, leadPad)
        return prefStr

    def getPreference(self):
        pref = copy.copy(self.__preference)
        return pref

    def _applyMoodWeights(self, mood, featureName, totalFrequencies):
        weightedFeature = 0.0

        
        weightedFeature += mood.getFrequency('Joy')*self.__preference['Joy'][featureName]
        weightedFeature += mood.getFrequency('Anger')*self.__preference['Anger'][featureName]
        weightedFeature += mood.getFrequency('Disgust')*self.__preference['Disgust'][featureName]
        weightedFeature += mood.getFrequency('Sadness')*self.__preference['Sadness'][featureName]
        weightedFeature += mood.getFrequency('Surprise')*self.__preference['Surprise'][featureName]
        weightedFeature += mood.getFrequency('Fear')*self.__preference['Fear'][featureName]
        weightedFeature = weightedFeature/totalFrequencies

        # because mode is a discrete value (its 'weight' is either 0 or 1) it must be calculated differently than features whose value is in the interval [0, 1]
        if featureName == 'mode':
            if weightedFeature >= .5:
                weightedFeature = 1
            else:
                weightedFeature = 0
            
        return weightedFeature


    # returns dict of audiofeatures key-value pairs to query Spotify
    # @param mood: moodstate object holding mood values
    def audioFeatureValues(self, mood):
        numTweets = mood.getFrequencyTotal()
        af = dict()
        af['dancability'] = self._applyMoodWeights(mood, 'dancability', numTweets)
        af['energy'] = self._applyMoodWeights(mood, 'energy', numTweets)
        af['loudness'] = self._applyMoodWeights(mood, 'loudness', numTweets)
        af['mode'] = self._applyMoodWeights(mood, 'mode', numTweets)
        af['accousticness'] = self._applyMoodWeights(mood, 'accousticness', numTweets)
        af['instrumentalness'] = self._applyMoodWeights(mood, 'instrumentalness', numTweets)
        af['valence'] = self._applyMoodWeights(mood, 'valence', numTweets)
        return af

    # updates the preferences table based on feedback that's passed as a parameter
    # @param audiofeatures: an AudioFeatures object from spotify
    def updateProfile(self, audiofeatures):
        #fixme: define update method
        print('fixme')