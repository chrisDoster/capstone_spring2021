from emotion_predictor import EmotionPredictor

class MoodState:
    def __init__(self):
        self.__emotionTotal = 0
        self.__emotionFrequency = dict()
        self.__emotionFrequency['Joy'] = 0
        self.__emotionFrequency['Fear'] = 0
        self.__emotionFrequency['Sadness'] = 0
        self.__emotionFrequency['Anger'] = 0
        self.__emotionFrequency['Surprise'] = 0
        self.__emotionFrequency['Disgust'] = 0
        self.__predictions = None
        
    @staticmethod
    def createState(tweets):
        ms = MoodState()
        ms.findFrequencies(tweets)
        return ms

    def findFrequencies(self, tweets):
        model = EmotionPredictor(classification='ekman', setting='mc', use_unison_model=True)
        self.__predictions = model.predict_classes(tweets)
        i = 0
        for index, row in self.__predictions.iterrows():
            self.__emotionFrequency[row['Emotion']] += 1

    def frequenciesStr(self):
        freqStr = 'EMOTION FREQUECIES \n'
        for key, value in self.__emotionFrequency.items():
            freqStr += key + ' ; count=' + str(value) + '\n'
        return freqStr

    def getPredictions(self):
        return self.__predictions

    def getFrequency(self, emo):
        return self.__emotionFrequency[emo]

    def getFrequencyTotal(self):
        total = 0
        total += self.getFrequency('Joy')
        total += self.getFrequency('Anger')
        total += self.getFrequency('Disgust')
        total += self.getFrequency('Sadness')
        total += self.getFrequency('Surprise')
        total += self.getFrequency('Fear')
        return total