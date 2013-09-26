#!/usr/bin/env python
# -*- coding: utf-8 -*-

import twitter
import MySQLdb
import pprint
import urllib
import urllib2
import base64
import sys
from datetime import datetime
from secrets import consumer_key, consumer_secret, auth_type, access_token_key, access_token_secret
from secrets import dbhost, dbuser, dbpass, dbname

class TwitterApiCall(object):
  api = twitter.Api(consumer_key = consumer_key,
                    consumer_secret = consumer_secret,
                    auth_type = auth_type)
                    #access_token_key = access_token_key,
                    #access_token_secret = access_token_secret)

  def GetRateLimits(self):
    return self.api.GetRateLimitStatus()

  def PrintRateLimit(self):
    pp = pprint.PrettyPrinter(depth=6)
    pp.pprint(self.GetRateLimits())

class DownloadFrenchTweets(TwitterApiCall):
  con = None

  def __init__(self):
    try:
      self.con = MySQLdb.connect(host = dbhost,
                                 user = dbuser,
                                 passwd = dbpass,
                                 db = dbname,
                                 charset = 'utf8')
      print "Connected to MySQL db %s:%s." % (dbhost, dbname)
    except Exception, e:
      print "Error connecting to MySQL db %s:%s: %s" % (dbhost, dbname, e)

  def __del__(self):
    if self.con: self.con.close()

  def GetCurrentLimit(self):
    limits = self.GetRateLimits()['resources']['search']['/search/tweets']
    return int(limits['remaining'])

  def SelectMaxTweetId(self):
    cur = self.con.cursor()
    try:
      cur.execute("SELECT MAX(`tweetid`) FROM tweets")
      firstid = cur.fetchone()[0]
      print "The last tweetid in table is %s." % firstid
    except Exception, e:
      firstid = None
    return firstid

  def InsertTweetsIntoDb(self):
    lat    = 45.776665 # Latitude and longitude of Clermont-Ferrand
    lng    = 3.07723
    radius = '400km'   # Radius of France territory
    count  = 100       # Number of tweets to retrieve (max. 100)
    lang   = 'fr'      # French language

    calls     = 0
    twits     = []
    ratelimit = self.GetCurrentLimit()
    max_id    = None
    since_id  = self.SelectMaxTweetId()

    sys.stdout.write('Executing Twitter API calls ')
    sys.stdout.flush()

    cur = self.con.cursor()

    while True:
      calls += 1
      inserted = 0
      if calls >= ratelimit - 2: break

      statuses = self.api.GetSearch(geocode = (lat, lng, radius),
                                    count = count,
                                    lang = lang,
                                    result_type = 'recent',
                                    include_entities = False,
                                    max_id = max_id,
                                    since_id = since_id)
      if (len(statuses) == 0): break
      #print "Number of tweets downloaded:\t%d." % len(statuses)

      for s in statuses:
        if (since_id is None): break
	
        date_object = datetime.strptime(s.created_at, '%a %b %d %H:%M:%S +0000 %Y')
	text = s.text.encode(encoding='ascii', errors='ignore').decode(encoding='ascii', errors='ignore')

        sql_vals = (s.id,
                    date_object.strftime('%Y-%m-%d %H:%M:%S'),
                    text.replace('\'', '\\\''),
                    ', '.join([h.text for h in s.hashtags]))

        sql  = 'INSERT INTO tweets (`tweetid`, `timestamp`, `text`, `hashtags`)'
        sql += 'VALUES (\'%s\', \'%s\', \'%s\', \'%s\')' % sql_vals

        try:
          cur.execute(sql)
          self.con.commit()
          inserted += 1
        except Exception as e:
          print "Exception while inserting tweet %s: %s" % (s.id, e)
          self.con.rollback()

      sys.stdout.write('.')
      sys.stdout.flush()

      twits.append(inserted)
      #print "Numer of tweets inserted:\t%d." % inserted
      max_id = min([s.id for s in statuses]) - 1

    print ""
    print "Executed %d calls to insert a total number of %d tweets." % (calls, sum(twits))
    for i in range(0, len(twits)):
      print "Call %d inserted %d tweets." % (i+1, twits[i])

if __name__ == "__main__":
  engine = DownloadFrenchTweets()
  #engine.SelectMaxTweetId()
  print engine.GetCurrentLimit()
  #engine.InsertTweetsIntoDb()