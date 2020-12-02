import tweepy
import time, random, json
from streamparse import Spout
import queue
import os
current_folder = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_folder, 'api.json')

with open(file_path) as f:
    twitter_api = json.loads(f.read())

consumer_key = twitter_api['consumer_key']
consumer_secret = twitter_api['consumer_secret_key']
access_token = twitter_api['access_token']
access_token_secret = twitter_api['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

class TweetListener(tweepy.StreamListener):

    def __init__(self, queue):
        super(TweetListener, self).__init__(api)
        self.queue = queue

    def on_status(self, status):

        if ('RT @' not in status.text):
            user_id = status.user.id_str
            try:
                self.queue.put(str(status.text), timeout = 0.01)
            except:
                pass

    def on_error(self, status_code):
        if status_code == 420:
            return False

if __name__ == '__main__':
    q = queue.Queue()
    stream_listener = TweetListener(q)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=["#nrc", "#caa"], is_async=True)

    freq = {}
    for i in range(1000000):
        try:
            tweet = q.get(timeout = 0.1)
            if tweet:
                if "#bitcoin" in tweet:
                    if "#bitcoin" in freq:
                        freq["#bitcoin"] += 1
                    else:
                        freq["#bitcoin"] = 1
                elif "#caa" in tweet:
                    if "#caa" in freq:
                        freq["#caa"] += 1
                    else:
                        freq["#caa"] = 1
                q.task_done()
        except queue.Empty:
            time.sleep(0.1)
            
    print(freq)
