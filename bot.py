import tweepy
import re
import random
import time
import os


API_KEY = "your_API_key"
API_SECRET = "your_secret_API_key"
ACCESS_KEY = "your_access_key"
ACCESS_SECRET = "your_secret_access_key"

USER_TO_COPY = "the_twitter_handle_of_the_account_you_want_to_copy_from"
NUM_OF_TWEETS = 2000  # number of latest tweets to be read from the bot

last_seen_mention_id = 1

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit = True)


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

    # word_dictionary = markov()

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


while True:
    print("***************************************")
    print('creating the markov chain dictionary...')
    word_dictionary = markov()

    # post randomly, once for every 150 tries
    if random.randint(1, 150) == 1:
        print('\nAWAKEN... GENERATING TWEET...')
        api.update_status(generate_tweet(word_dictionary))

    print('\nsleep mode for 1 minute...')
    print("***************************************")

    time.sleep(60)
