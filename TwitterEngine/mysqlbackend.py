__author__ = "Andrea Biancini"
__date__ = "October 2, 2013"

import MySQLdb
import pprint
import sys
import json

from datetime import datetime

from backend import Backend, BackendError
from secrets import dbhost, dbuser, dbpass, dbname


class MySQLBackend(Backend):
  con = None
  cur = None

  def __init__(self):
    try:
      self.con = MySQLdb.connect(host = dbhost,
                                 user = dbuser,
                                 passwd = dbpass,
                                 db = dbname,
                                 charset = 'utf8')
      print "Connected to MySQL db %s:%s." % (dbhost, dbname)
      self.cur = self.con.cursor()
    except Exception as e:
      raise BackendError("Error connecting to MySQL db %s:%s: %s" % (dbhost, dbname, e))

  def __del__(self):
    if self.con: self.con.close()

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
        raise BackendError("Exiting because tried to insert a tweet already present in the DB: %s", sql_vals[0])
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
        if row[0] == 'max_id': ids[0] = row[0]
        elif row[0] == 'since_id': ids[1] = row[0]

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
