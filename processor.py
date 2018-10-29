from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import json
import time

import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

terms = {}
debug = False
host = "localhost"
port = 8002

smooth_fast = None
smooth_slow = None
decay_window = None


# Read config values
with open('config.json','r') as f:
    data = json.loads(f.read())
    debug = data["config"]["debug"]
    port = data["config"]["port"]
    host = data["config"]["host"]

    smooth_fast = data["output"]["smooth_fast"]
    decay_window = data["output"]["decay_window"]
    smooth_slow = data["output"]["smooth_slow"]


    for k, v in data["keywords"].items():
        for i in v:
            terms[i] = k

# Create a local StreamingContext with two working thread and batch interval of 1 second
sc = SparkContext("local[2]", "NetworkWordCount")
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 1)
ssc.checkpoint("checkpoint")

# Create a DStream that will connect to hostname:port, like localhost:9999
lines = ssc.socketTextStream(host, port)


# define the update function
def decaying_window(newVals, currentAvg):
    if currentAvg is None:
       currentAvg = sum(newVals)/len(newVals)

    if len(newVals) > 0:
        return (1.0-1e-6)*currentAvg + sum(newVals)/len(newVals) 
    return currentAvg

def smooth_update_fast(newVals, currentVal):

    if len(newVals) == 0 and currentVal is None:
        return 0

    if currentVal is None:
       currentVal = sum(newVals)/len(newVals)
       return currentVal

    if len(newVals) == 0:
        return currentVal

    return 0.99*currentVal + 0.01*sum(newVals)/len(newVals)

def smooth_update_slow(newVals, currentVal):
    if len(newVals) == 0 and currentVal is None:
        return 0

    if currentVal is None:
       currentVal = smooth_update_internal(newVals, currentVal)
       return currentVal

    return smooth_update_internal(newVals, currentVal)

def smooth_update_internal(newVals, currentVal):
    for val in newVals:
        if currentVal is None:
            currentVal = val
        currentVal = 0.99*currentVal + 0.01*val

    return currentVal

def splitTweets(tweet):

    global sia

    tweet = tweet.lower()

    sentimentScore = sia.polarity_scores(tweet)["compound"]

    for k in terms.keys():
        if k in tweet:
            return (terms[k], sentimentScore)
    return ("no category", sentimentScore)

def toFile(filename, x):
    with open(filename,'w') as f:
        f.write(x)


#reduceByKeyWindow? <-- TODO?
pscores = lines.map(lambda x: splitTweets(x))


def resout(filename, rdd):
    """
    Writes the summary (current values) to a file
    """
    with open(filename,'w') as f:
        dictionary = rdd.collectAsMap()

        for key, value in dictionary.items():
            f.write(str(key) + " " + str(value) + "\n")

def resout_log(filename, rdd):
    """
    Writes a continuous log to a file
    """
    with open(filename,'a') as f:
        dictionary = rdd.collectAsMap()
        dictionary["time"] = int(time.time())
        f.write(json.dumps(dictionary) + "\n")

if smooth_fast != None :
    smooth_count_fast = pscores.updateStateByKey(smooth_update_fast)
    smooth_count_fast.foreachRDD(lambda x,y : resout_log(smooth_fast,y))

if smooth_slow != None:
    smooth_count_slow = pscores.updateStateByKey(smooth_update_slow)
    smooth_count_slow.foreachRDD(lambda x,y : resout_log(smooth_slow,y))

if decay_window != None:
    decay_window_count= pscores.updateStateByKey(decaying_window)
    decay_window_count.foreachRDD(lambda x,y : resout_log(decay_window,y))

    if debug:
        decay_window_count.pprint()


ssc.start()             # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
