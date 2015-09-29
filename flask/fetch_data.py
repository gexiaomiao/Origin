#!/usr/bin/env python

# import all required modules
import json
from requests.auth import HTTPBasicAuth
from urllib2 import urlopen, Request
import os
import requests
import time
import gzip
from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection
from cqlengine.management import sync_table

# define model for desired table
class userfollow(Model):
  username = columns.Text(primary_key=True)
  following = columns.List(columns.Text)
  def __repr__(self):
    return '%s %d' % (self.username, self.following)

# setup connection to Cassandra and sybc table
connection.setup(['52.8.127.252', '52.8.41.216'], "watch_events")
sync_table(userfollow)

start = time.time()

# access token
github_pass_alvin = os.environ['my_pass']

following_url = "https://api.github.com/users/"

per_page="&per_page=100"

# call github API and return following list
# return False if username doesn't exist
i=0
def get_following(url_tail, user, following, page):
  global github_pass_alvin
  json_response = []
  github_pass = github_pass_alvin
  try:
    request = Request(following_url + user + "/following" + url_tail + per_page)
    request.add_header('Authorization', 'token %s' % github_pass)
    response = urlopen(request, timeout=5)
    json_response = json.loads(response.read())
  except requests.exceptions.Timeout as e:
    time.sleep(30)
    return False
  except requests.exceptions.ConnectionError as e:
    time.sleep(30)
    return False
  except requests.exceptions.HTTPError as e:
    time.sleep(30)
    return False
  except Exception, e:
    print e
    return False
  if json_response == [] or page==10:
    return following
  else:
    following += json_response
    page +=1
    get_following("?page="+str(page), user, following, page)
    return following

# filter json response and extract just usernames
def follows(x):
    try:
        following_list = []
        if x == []:
            return following_list
        else:
            for user in x:
                following_list.append(user['login'])
            return following_list
    except Exception as e:
        print x, e
    return following_list

# call the API function and save results to cassandra
def get_user_following(username):
    user = username
    following = []
    following_dict = {}
    following = get_following("?page=1", user, [], 1)
    if not following:
      return False
    following_dict["login"] = user
    following_dict["following"] = following
    userfollow.create(username=user, following = follows(following))
    return True

if __name__ == "__main__":
  main()
