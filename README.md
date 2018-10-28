# Introduction

## Prerequisites

* Apache Spark 2.3.2 with Hadoop ([download spark](http://spark.apache.org/downloads.html))
* Java 8 ([installation tutorial](https://tecadmin.net/install-oracle-java-8-ubuntu-via-ppa/))
* Apache 2  Server (optional)

> If you want to print to a local webserver such as Apache, make sure to
enable write access using `chown -R user:user /var/www/html`. If you don't use Apache,
please make sure to change output files that you have permission to write to.

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

## Configuration file

```
{
    "keywords": {
        "trump": ["potus","trump"],
        "hillary": ["hillary"],
        "billgates": ["billgates"],
        "putin": ["putin"],
        "merkel": ["merkel"],
        "elonmusk": ["elonmusk"]
    },
    "twitter": {
        "access_token": "",
        "access_token_secret": "",
        "consumer_key": "",
        "consumer_secret": ""
    },
    "output":{
        "smooth_fast":"/var/www/html/index.txt",
        "smooth_slow": "/var/www/html/index2.txt"
    },
    "config": {
        "debug": true,
        "host": "localhost",
        "port": 8002
    }
}
```