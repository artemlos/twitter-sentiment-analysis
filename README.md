# Introduction

## Prerequisites

* Apache Spark 2.3.2 with Hadoop ([download spark](http://spark.apache.org/downloads.html))
* Java 8 ([installation tutorial](https://tecadmin.net/install-oracle-java-8-ubuntu-via-ppa/))
* Apache 2  Server (optional, if you want others to access their result)
* Twitter API keys ([apply here](https://developer.twitter.com/en/apply-for-access))
* Python3 packages: `tweepy`, `twython` and `nltk` (there might be some more, please check error messages if such would occur)

> If you want to print to a local webserver such as Apache, make sure to
enable write access using `chown -R user:user /var/www/html`. If you don't use Apache,
please make sure to change to output files that you have permission to write to.

## Before first run
1. Please review `shell.sh` to make sure that correct folders are provided to Apache Spark and Python 3.
2. Create a `config.json`, set your twitter access tokens and change the keywords (see _Configuration file_ section).

## Run

In terminal 1:
```
$ python3 tweetread.py
```

In terminal 2:
```
$ source shell.sh
spark-submit processor.py
```

## Debugging/Tips
* We recommend to turn off info messages to make the output clearer. See [here](https://stackoverflow.com/a/34306251)
how it can be accomplished.
* If terminal 1 prints errors, please restart it.

## Code specific
* When the result is written to file, there are two functions available, `resout` and `resout_log`. The first
one will only write the current state to a file whereas the latter will append the result (so that you can analyse it later).
* If you want to dedicate most of the resources of the computer on this, we recommend to replace `local[2]` to `local[*]` when
initializing the spark context and increase memory available to Spark, which can be achieved as shown below (in terminal 2):

```
$ source shell.sh
spark-submit --num-executors 4 --driver-memory 64g --executor-memory 64g processor.py
```

## Configuration file
The configuration file has a structure similar to the one below. To be able to run the code, you need at least the twitter
tokens and to ensure that the output files are writable.

Keywords are configured as follows. Let's say you want to track `trump`. We know that people may refer to trump either by `potus` or `trump`.
Therefore, we define these aliases in a list, i.e. `"trump": ["potus","trump"]`.

```
{
    "keywords": {
        "trump": ["potus","trump"],
        "hillary": ["hillary"],
        "billgates": ["billgates"],
        "putin": ["putin"],
        "merkel": ["merkel"],
        "elonmusk": ["elonmusk"],
        "junker_eu" : ["junckereu", "junker", "jean claude junker"],
        "donald_tusk_eu":["eucopresident", "donald tusk"],
        "brexit" : ["brexit"],
        "theresa_may":["theresa_may", "theresa may"]
    },
    "twitter": {
        "access_token": "",
        "access_token_secret": "",
        "consumer_key": "",
        "consumer_secret": ""
    },
    "output":{
        "smooth_fast":"/var/www/html/index.txt",
        "smooth_slow": null,
        "decay_window": "/var/www/html/decay_window.txt",
        "actual_val" : "/var/www/html/actual_val.txt"
    },
    "config": {
        "debug": false,
        "host": "localhost",
        "port": 8002
    }
}
```

## Future work
Spark has recently added a continuous processing feature, which can be used instead of using mini-batch. At the time of writing, it's in experimental phase.
Please read more [here](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#continuous-processing).
