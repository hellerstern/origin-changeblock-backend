import pandas as pd
import snscrape.modules.twitter as sntwitter
import itertools
import os
import pandas as pd
import numpy as np
import re

from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")


def scrap(country, hash_tags, n):
    df_country = []
    for i in range(0, len(hash_tags)):
        df_country.append(pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
            f'{hash_tags[i]} near:{country} within:4000km lang:en').get_items(), n)))
        df = pd.concat(df_country, axis=0, sort=False)
        df = df.reset_index(drop='index')
    return df


def listings(Allcountry, hash_tags, n):
    concat_data = []
    for country in Allcountry:

        data = scrap(country, hash_tags, n)
        data['country'] = country
        concat_data.append(data)
        df = pd.concat(concat_data, axis=0, sort=False)
        df = df.reset_index(drop='index')
    return df


def clean_tweet(tweet):
    temp = tweet.lower()
    temp = re.sub("@[A-Za-z0-9_]+", "", temp)
    temp = re.sub("#[A-Za-z0-9_]+", "", temp)
    temp = re.sub(r"http\S+", "", temp)
    temp = re.sub(r"www.\S+", "", temp)
    temp = re.sub('[()!?]', ' ', temp)
    temp = re.sub('\[.*?\]', ' ', temp)
    temp = re.sub("[^a-z0-9]", " ", temp)
    return temp


def analysis(df):
    """
    input: dataframe of tweets
    output: a tuple containing 2 items 
        1: sentiment_scores: a list of json where each element has 2 keys, label and score
        2: average_sentiment_score: average of all the sentiment scores 
    """
    df = df[df['lang'] == 'en']
    tweets = df['rawContent'].tolist()
    tweets = [clean_tweet(tweet) for tweet in tweets]
    sentiment_scores = sentiment_pipeline(tweets)
    print(sentiment_scores)
    average_sentiment_score = 0
    # convert 0-5 scale
    for i in sentiment_scores:
        i['score'] = 1-i['score']
        if i['label'] == 'POSITIVE':
            i['score'] *= 2.5
        else:
            i['score'] = 5-(i['score']*2.5)
        average_sentiment_score += i['score']

    for i in range(len(tweets)):
        print(tweets[i], sentiment_scores[i])
    average_sentiment_score /= len(sentiment_scores)
    return sentiment_scores,  average_sentiment_score

# hash_tags =['#suicide']
# Allcountry = ['pakistan']
# df= listings(Allcountry, hash_tags, 10)
# print(analysis(df))
