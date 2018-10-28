from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import json

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


# Read config values
with open('config.json','r') as f:
    data = json.loads(f.read())
    debug = data["config"]["debug"]
    port = data["config"]["port"]
    host = data["config"]["host"]

    smooth_fast = data["output"]["smooth_fast"]
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
def updateTotalCount(newVals, currentVal):
    if currentVal is None:
       currentVal = float(0.0)

    if len(newVals) > 0:
        return (1.0-1e-6)*currentVal + mean(newVals) #sum(currentCount, countState)
    return (1.0-1e-6)*currentVal

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

    """
    if "trump" in tweet or "potus" in tweet:
        return ("trump", sentimentScore)
    elif "hillary" in tweet:
        return ("hillary", sentimentScore)
    elif "billgates" in tweet:
        return ("billgates", sentimentScore)
    elif "putin" in tweet or "путин" in tweet:
        return ("putin", sentimentScore)
    elif "merkel" in tweet:
        return ("merkel", sentimentScore)
    elif "elonmusk" in tweet:
        return ("elonmusk", sentimentScore)

    """

def toFile(filename, x):
    with open(filename,'w') as f:
        f.write(x)



# Split each line into words
# reduce by key will be used used if we have multiple terms
#pscores = lines.map(lambda line: float(sia.polarity_scores(line)["compound"])).reduce(lambda x,y: x+y).map(lambda x: ("trump", x))

#reduceByKeyWindow? <-- TODO?
pscores = lines.map(lambda x: splitTweets(x)).reduceByKey(lambda x,y: x+y)

smooth_count_fast = pscores.updateStateByKey(smooth_update_fast)
smooth_count_slow = pscores.updateStateByKey(smooth_update_slow)

if debug:
    smooth_count_fast.pprint()


def resout(filename, rdd):
    with open(filename,'w') as f:
        dictionary = rdd.collectAsMap()

        for key, value in dictionary.items():
            f.write(str(key) + " " + str(value) + "\n")

if smooth_fast != None :
    smooth_count_fast.foreachRDD(lambda x,y : resout(smooth_fast,y))

if smooth_slow != None:
    smooth_count_slow.foreachRDD(lambda x,y : resout(smooth_slow,y))


ssc.start()             # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
