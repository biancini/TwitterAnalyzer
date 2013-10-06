__author__ = "Andrea Biancini"
__date__ = "October 2, 2013"

import pprint
import sys
import requests
import json
import pprint
import StringIO

from datetime import datetime

from backend import Backend, BackendError
from secrets import dbhost, dbuser, dbpass, dbname


class ElasticSearchBackend(Backend):
  elasticsearch_server = 'http://localhost:9200'

  def SelectMaxTweetId(self):
    try:
      self.cur.execute("SELECT MAX(`tweetid`) FROM tweets")
      firstid = self.cur.fetchone()[0]

      print "The last tweetid in table is %s." % firstid
      return firstid
    except Exception as e:
      raise BackendError("Error while retrieving firstid: %s" % e)

  def InsertTweetIntoDb(self, sql_vals):
    try:
      sql  = 'INSERT INTO tweets (`tweetid`, `timestamp`, `text`, `hashtags`, `user_location`, `latitude`, `longitude`) '
      sql += 'VALUES (%s, \'%s\', \'%s\', \'%s\', \'%s\', %s, %s)' % sql_vals

      self.cur.execute(sql)
      self.con.commit()
      return 1
    except Exception as e:
      code, msg = e
      if code == 1062:
        self.con.rollback()
        raise BackendError("Tried to insert a tweet already present in the DB: %s" % sql_vals[0])
      else:
        print "Exception while inserting tweet %s: %s" % (sql_vals[0], e)

      self.con.rollback()
      return 0

  def GetKmls(self):
    try:
      self.cur.execute("SELECT NOM_REG, KML FROM french_deps")
      rows = self.cur.fetchall()

      kmls = []
      for row in rows:
        kmls.append((row[0], row[1]));

      return kmls
    except Exception as e:
      raise BackendError("Error while retrieving kmls from DB: %s" % e)

  def GetLastCallIds(self):
    try:
      self.cur.execute("SELECT `key`, `value` from lastcall")
      rows = self.cur.fetchall()

      ids = [None, None]
      for row in rows:
        if row[0] == 'max_id': ids[0] = row[1]
        elif row[0] == 'since_id': ids[1] = row[1]

      return ids
    except Exception as e:
      raise BackendError("Error while retrieving last call ids from DB: %s" % e)

  def UpdateLastCallIds(self, max_id = None, since_id = None):
    print "Updating lastcall with values max_id = %s and since_id = %s." % (max_id, since_id)
    try:
      if max_id:
        sql = "UPDATE lastcall SET `value` = '%s' WHERE `key` = 'max_id'" % max_id
      else:
        sql = "UPDATE lastcall SET `value` = NULL WHERE `key` = 'max_id'"
      self.cur.execute(sql)
      self.con.commit()

      if since_id:
        sql = "UPDATE lastcall SET `value` = '%s' WHERE `key` = 'since_id'" % since_id
      else:
        sql = "UPDATE lastcall SET `value` = NULL WHERE `key` = 'since_id'"
      self.cur.execute(sql)
      self.con.commit()
    except Exception as e:
      raise BackendError("Error while updating last call ids into DB: %s" % e)

  def GetAllTweetCoordinates(self):
    try:
      #self.cur.execute("SELECT `timestamp`, `latitude`, `longitude` FROM tweets ORDER BY `timestamp` LIMIT 100")
      self.cur.execute("SELECT `timestamp`, `latitude`, `longitude` FROM tweets ORDER BY `timestamp`")
      rows = self.cur.fetchall()

      tweets = []
      for row in rows:
        tweets.append([row[0], row[1], row[2]]);

      return tweets
    except Exception as e:
      raise BackendError("Error while retrieving tweet coordinates from DB: %s" % e)

  def GetLocations(self):
    try:
      self.cur.execute("SELECT user_location, COUNT(*) AS `number` FROM tweets WHERE latitude IS NULL GROUP BY user_location ORDER BY number DESC")
      rows = self.cur.fetchall()

      locations = []
      for row in rows:
        locations.append(row[0]);

      return locations
    except Exception as e:
      raise BackendError("Error while retrieving locations from DB: %s" % e)

  def UpdateCoordinates(self, location, lat, lng):
    print "Updating coordinate for location %s: [%s, %s]." % (location, lat, lng)
    try:
      self.cur.execute("UPDATE tweets SET latitude = %s, longitude = %s WHERE user_location = '%s'" % (lat, lng, location.replace('\\', '\\\\').replace('\'', '\\\'')))
      self.con.commit()
    except Exception as e:
      raise BackendError("Error while updating coordinates for location into DB: %s" % e)

  def InsertFrenchDepartments(self, vals):
    print "Inserting row for %s, %s." % (vals[2], vals[4])
    try:
      data = { 'CODE_DEPT' : vals[1],
               'NOM_DEPT'  : vals[2],
               'CODE_CHF'  : vals[3],
               'NOM_CHF'   : vals[4],
               'CODE_REG'  : vals[5],
               'NOM_REG'   : vals[6],
               'KML'       : vals[7] }
      data_json = json.dumps(data, indent=2)
      host = "%s/twitter/french_depts/%s" % (self.elasticsearch_server, vals[0])
      req = requests.put(host, data=data_json)
      ret = json.loads(req.content)
      if not ret["ok"]: raise BackendError("Insert not ok")
    except Exception as e:
      raise BackendError("Error while inserting French department into ElasticSearch: %s" % e)

  def GetFrenchDepartments(self):
    print "Retrieving all French departments"
    try:
      data = { "query" : { "match_all" : { } } }
      data_json = json.dumps(data, indent=2)
      # TODO manage pagination and eliminate size 100
      host = "%s/twitter/french_depts/_search?size=100" % self.elasticsearch_server
      req = requests.get(host, data=data_json)
      ret = json.loads(req.content)
      rows = []
      for hit in ret['hits']['hits']:
        curhit = []
        if 'NOM_REG' in hit['_source'] and 'KML' in hit['_source']:
          curhit.append(hit['_source']['NOM_REG'].replace('\\\'', '\''))
          curhit.append(hit['_source']['KML'].replace('\\\'', '\''))
          rows.append(curhit)

      return rows
    except Exception as e:
      raise BackendError("Error while retrieving French departments from ElasticSearch: %s" % e)
