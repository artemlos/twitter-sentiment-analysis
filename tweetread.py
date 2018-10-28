import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import socket
import json

# these values come from the config
access_token = None
access_token_secret = None
consumer_key = None
consumer_secret = None
track = []
debug = False

class TweetsListener(StreamListener):

  def __init__(self, csocket):
      self.client_socket = csocket

  def on_data(self, data):
      try:
          msg = json.loads(data)
          if debug:
            print(msg['text'].encode('utf-8'))
          self.client_socket.send(msg['text'].encode('utf-8'))
          return True
      except BaseException as e:
          print("Error on_data: %s" % str(e))
      return True

  def on_error(self, status):
      print(status)
      return True

def sendData(c_socket):
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)

  twitter_stream =Stream(auth, TweetsListener(c_socket)) #Stream(auth, TweetsListener(c_socket))
  twitter_stream.filter(track=track)

if __name__ == "__main__":

    host = "localhost"          # Get local machine name
    port = 8002                 # Reserve a port for your service.

    with open('config.json','r') as f:
        data = json.loads(f.read())
        access_token = data["twitter"]["access_token"]
        access_token_secret = data["twitter"]["access_token_secret"]
        consumer_key = data["twitter"]["consumer_key"]
        consumer_secret = data["twitter"]["consumer_secret"]
        track = list(data["keywords"].keys())
        debug = data["config"]["debug"]
        port = data["config"]["port"]
        host = data["config"]["host"]


    s = socket.socket()         # Create a socket object
    s.bind((host, port))        # Bind to the port

    print("Listening on port: %s" % str(port))

    s.listen(5)                 # Now wait for client connection.
    c, addr = s.accept()        # Establish connection with client.

    print( "Received request from: " + str( addr ) )

    sendData( c )
