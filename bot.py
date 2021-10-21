import tweepy
import re
import random
import time
import datetime
import os
from os import environ


API_KEY = environ['API_KEY']
API_SECRET = environ['API_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

USER_TO_COPY = environ['USER_TO_COPY']
NUM_OF_TWEETS = 2000  

last_seen_mention_id = 1451240772242653192

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


# function that grabs the last tweets from a user and returns all their words to a list
def fetch_words():
    sentences = []

    for tweet in tweepy.Cursor(api.user_timeline, screen_name=USER_TO_COPY, tweet_mode="extended").items(NUM_OF_TWEETS):
        if not hasattr(tweet, 'retweeted_status'):
            # remove mention handles (@sth) and URLs, if any
            t = re.sub(r'(@\S+)|(http\S+)', '', tweet.full_text.lower())
            sentences.append(t)

    # create a list of individual words from the sentences/tweets
    words = []

    for sentence in sentences:
        for word in sentence.split():
            words.append(word)

    return words


# function that creates sets consisting of 3 words each from the word list
def triples():
    words = fetch_words()

    if len(words) < 3:
        return

    for i in range(len(words) - 2):
        yield (words[i], words[i + 1], words[i + 2])


# function that creates the markov chains and returns the generated dictionary
def markov():
    word_dictionary = {}

    for word_1, word_2, word_3 in triples():
        key = (word_1, word_2)
        if key in word_dictionary:
            word_dictionary[key].append(word_3)
        else:
            word_dictionary[key] = [word_3]

    return word_dictionary


# function that uses the markov chain dictionary to create tweets
def generate_tweet(word_dictionary):
    words = fetch_words()

    size = random.randint(3, 50)  # min and max words in a tweet

    # pick a random word of the list to start the sentence
    seed = random.randint(0, len(words) - 3)
    seed_word, next_word, = words[seed], words[seed + 1]
    word_1, word_2 = seed_word, next_word

    #word_dictionary = markov()

    status_words = []

    # create the sentence of the tweet, word by word
    for i in range(size):
        status_words.append(word_1)
        word_1, word_2 = word_2, random.choice(word_dictionary[(word_1, word_2)])

    status_words.append(word_2)

    status = ' '.join(status_words)

    # if the status is too big for twitter, replace it with a random emoji
    if(len(status) > 240):
        status = random.choice(['\U0001F97A', '\U0001F644', '\U0001F912', '\U0001F61F', '\U0001F914', '\U0001F440', '\U0001F60F', '\U0001F4AF'])

    print('\t\'' + status + '\'')

    return status


# function that searches for mentions and responds with a generated tweet
def reply_to_mentions(word_dictionary):
    global last_seen_mention_id

    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=last_seen_mention_id, tweet_mode="extended").items():
        last_seen_mention_id = tweet.id

        if tweet.user.screen_name != api.me().screen_name and tweet.favorited == False:
            print('\nreplying to ' + tweet.user.screen_name + '...')
            print('last seen mention ID: ' + str(last_seen_mention_id) + '\n')
            api.update_status('@' + tweet.user.screen_name + ' ' + generate_tweet(word_dictionary), tweet.id)
            api.create_favorite(tweet.id)


while True:
    print('***************************************')
    print(datetime.datetime.now())
    print('***************************************')
    word_dictionary = markov()     
    reply_to_mentions(word_dictionary)

    # post randomly, once for every 400 tries
    if random.randint(1, 150) == 1:
        print('creating the markov chain dictionary...')
        print('generating post...')
        api.update_status(generate_tweet(word_dictionary))
    print('\nsleep mode for 1 minute...')
    print('***************************************\n')

    time.sleep(60)
