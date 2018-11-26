import json
import os
import re

import requests
import tweepy

from superform import db

FIELDS_UNAVAILABLE = ["Title"]
CONFIG_FIELDS = ["consumer_key", "consumer_secret", "access_token_key", "access_token_secret"]

AUTH_FIELDS = False
POST_FORM_VALIDATIONS = {}

def run(publishing, channel_config):

    # To do : Error management

    json_data = json.loads(channel_config)

    for field in CONFIG_FIELDS:
        if json_data.get(field) is None:
            print("Missing : {0}".format(field))
            return

    cfg = {
        "consumer_key": str(json_data['consumer_key']),
        "consumer_secret": str(json_data['consumer_secret']),
        "access_token": str(json_data['access_token_key']),
        "access_token_secret": str(json_data['access_token_secret'])
    }

    api = get_api(cfg)
    link_url = publishing.link_url
    text = publishing.description

    if link_url is not '':
        text = text + ' '
        text = text + link_url
    tweets = tweet_split(text, (',', '!', '?', ':', ';', '\n'))
    image_url = publishing.image_url
    if image_url is '':
        try:
            tweet_id = None
            for tweet in tweets:
                if tweet_id is None:
                    tweet_id = api.update_status(status=tweet)
                else:
                    tweet_id = api.update_status(tweet, tweet_id.id_str)
        except tweepy.TweepError as e:
            print(e.reason)
    else:
        filename = 'img.jpg'
        request = requests.get(image_url, stream=True)
        if request.status_code == 200:
            with open(filename, 'wb') as image:
                for req in request:
                    image.write(req)
            try:
                tweet_id = None
                for tweet in tweets:
                    if tweet_id is None:
                        tweet_id = api.update_with_media(filename, status=tweet)
                    else:
                        tweet_id = api.update_status(tweet, tweet_id.id_str)
            except tweepy.TweepError as e:
                print(e.reason)
            os.remove(filename)
        else:
            print("Cant load the image")
    publishing.state = 1
    db.session.commit()


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)


def get_urls(text):
    pattern = r'((?:http[s]?:/{2})?(?:w{3}\.)?(?:\w+\.)+(?:com|fr|be|io|gov|net|tv|uk|ch|de|nl|lu)(?:/[^\s]+)?)'
    return re.findall(pattern, text)


def tweet_split(text, separators):
    my_str = text

    tweets = []
    limit = 280

    if len(text) <= limit:
        tweets += [text]
    else:
        limit -= 4
        urls = get_urls(text)
        url_index = []
        url_len = []
        for url in urls:
            url_index.append(text.find(url))
            url_len.append(len(url))

        for sep in separators:
            my_str = my_str.replace(sep, '.')

        sentences = my_str.split(".")
        index = 0  # index général dans text
        nbTweet = 0  # nombre de tweets
        count = 0  # taille du tweet actuel
        temp = ""  # tweet temporaire

        for s in sentences:
            done = False
            if (len(s) + 1) > limit:
                if separators == ' ':
                    print("Split between characters")
                    return [text[i:i+280] for i in range(0, len(text), 280)]
                else:
                    print("Split between words")
                    return tweet_split(text, ' ')
            else:
                if not url_index:  # if no url in text
                    if (count + len(s) + 1) < limit:  # tweet small enough
                        temp += text[index: index + len(s) + 1]
                        count += len(s) + 1
                        index += len(s) + 1
                    else:
                        tweets += [temp]
                        if text[index] == ' ':
                            temp = text[index + 1: index + len(s) + 1]
                            count = len(s)
                            index += len(s) + 1
                        else:
                            temp = text[index: index + len(s) + 1]
                            count = len(s) + 1
                            index += len(s) + 1
                        nbTweet += 1
                else:  # if url in text
                    for (i, l) in zip(url_index, url_len):
                        # url in this sentence :
                        if (i <= index <= i + l) or (i <= index + len(s) + 1 <= i + l):
                            done = True
                            if limit - count <= l + i - index + 1:  # no room in this tweet to add until end of url
                                if limit - count <= i - index + 1:  # no room to add until start of url then start a new one
                                    tweets += [temp]
                                    nbTweet += 1
                                    temp = ""
                                # enough room in this tweet to add until start of url
                                if text[index] == ' ':
                                    index += 1
                                temp += text[index: i]
                                tweets += [temp]
                                nbTweet += 1
                                index += len(s) + 1
                                temp = text[i: index]  # start of a new tweet
                                count = index - i
                            else:  # url can be put in full in this tweet
                                if len(s) > limit - count:
                                    # full sentence can't be put in this tweet, so take until end of url, then start new one
                                    temp += text[index: i + l]
                                    tweets += [temp]
                                    nbTweet += 1
                                    temp = text[i + l + 1: index + len(s) + 1]
                                    index += len(s) + 1
                                    count = index - i
                                else:
                                    temp += text[index: index + len(s) + 1]
                                    count += len(s) + 1
                                    index += len(s) + 1

                    # url not in this sentence
                    if not done:
                        if (count + len(s) + 1) < limit:  # tweet small enough to put a sentence
                            temp += text[index: index + len(s) + 1]
                            count += len(s) + 1
                            index += len(s) + 1
                        else:  # tweet too big
                            tweets += [temp]
                            if text[index] == ' ':
                                temp = text[index + 1: index + len(s) + 1]
                                count = len(s)
                                index += len(s) + 1
                            else:
                                temp = text[index: index + len(s) + 1]
                                count = len(s) + 1
                                index += len(s) + 1
                            nbTweet += 1

        tweets += [temp]

    if not len(tweets) == 1:
        for i in range(0, len(tweets)):
            tweets[i] = str(i + 1) + '/' + str(len(tweets)) + ' ' + tweets[i]

    return tweets

# Methods from other groups :

def post_pre_validation(post):
    return 1;

def authenticate(channel_name, publishing_id):
    return 'AlreadyAuthenticated'