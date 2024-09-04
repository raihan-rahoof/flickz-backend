import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)

    if sentiment_score['compound'] >=0.05:
        return 'Positive'
    elif sentiment_score['compound'] <=0.05:
        return 'Negative'
    else:
        return 'Average'