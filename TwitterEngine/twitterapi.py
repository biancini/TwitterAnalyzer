#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
import sys
import json

import os
root_path = os.path.abspath(os.path.join(__file__, '..', '..'))
lib_path = os.path.join(root_path, 'lib')
sys.path.insert(0, lib_path)

from datetime import datetime
from TwitterAPI import TwitterAPI
from geopy import geocoders

from secrets import consumer_key, consumer_secret, access_token_key, access_token_secret


class TwitterApiCall(object):
  api = None

  def __init__(self, auth_type='oAuth2'):
    if auth_type == 'oAuth2':
      self.api = TwitterAPI(consumer_key = consumer_key,
                            consumer_secret = consumer_secret,
                            auth_type = auth_type)
    else:
      self.api = TwitterAPI(consumer_key = consumer_key,
                            consumer_secret = consumer_secret,
                            auth_type = auth_type,
                            access_token_key = access_token_key,
                            access_token_secret = access_token_secret)

  def GetRateLimits(self):
    params = {}
    response = self.api.request('application/rate_limit_status', params)
    return json.loads(response.text)

  def PrintRateLimit(self):
    pp = pprint.PrettyPrinter(depth=6)
    pp.pprint(self.GetRateLimits())

  def Geolocate(self, location):
    #g = geocoders.GoogleV3(google_clientid, google_secret)
    #g = geocoders.MapQuest(api_key=mapquest_appid)
    g = geocoders.GeoNames()
 
    try:
      for place, (lat, lng) in g.geocode(location, exactly_one=False):
        #print "Computed coordinates for %s: %s, %s." % (location, lat, lng)
        coordinates= [str(lat), str(lng)]
    except Exception as e:
      print "Error while geocoding: %s" % e
      coordinates = ['NULL', 'NULL']

    return coordinates

  def FromTweetToSQLVals(self, tweet, geolocate=True, exclude_outs=True):
    date_object = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    text = tweet['text'].encode(encoding='ascii', errors='ignore').decode(encoding='ascii', errors='ignore')
    location = tweet['user']['location']

    if tweet['coordinates'] and tweet['coordinates']['type'] == 'Point':
      coordinates = tweet['coordinates']['coordinates']
    elif geolocate:
      coordinates = self.Geolocate(location)
    else:
      coordinates = ['NULL', 'NULL']

    sql_vals = (tweet['id'],
                date_object.strftime('%Y-%m-%d %H:%M:%S'),
                text.replace('\\', '\\\\').replace('\'', '\\\''),
                ', '.join([h['text'] for h in tweet['entities']['hashtags']]).replace('\\', '\\\\').replace('\'', '\\\''),
                location.replace('\\', '\\\\').replace('\'', '\\\''),
                coordinates[0],
                coordinates[1])

    return sql_vals

