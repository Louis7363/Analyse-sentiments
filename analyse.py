from textblob import TextBlob

def analyse_sentiment(text):
    analysis = TextBlob(text)
    # Renvoie la polarité : -1 = négatif, +1 = positif
    return analysis.sentiment.polarity

tweet = "I am so happy today!"
print(analyse_sentiment(tweet))  # Par exemple, cela pourrait donner 0.8 (positif)
