__author__ = "Andrea Biancini"
__date__ = "October 2, 2013"

class BackendChooser(object):
  @staticmethod
  def GetBackend(logger):
    # from mysqlbackend import MySQLBackend
    # backend = MySQLBackend(logger)
    from elasticsearchbackend import ElasticSearchBackend
    backend = ElasticSearchBackend(logger)
    return backend
  
class Backend(object):
  logger = None
  
  def __init__(self, logger):
    self.logger = logger
    
  def BulkInsertTweetIntoDb(self, vals):
    raise NotImplementedError
  
  def InsertTweetIntoDb(self, sql_vals):
    raise NotImplementedError

  def GetKmls(self):
    raise NotImplementedError

  def GetLastCallIds(self):
    raise NotImplementedError

  def UpdateLastCallIds(self, max_id=None, since_id=None):
    raise NotImplementedError

  def GetAllTweetCoordinates(self):
    raise NotImplementedError

  def UpdateCoordinates(self, location, lat, lng):
    raise NotImplementedError

  def GetLocations(self):
    raise NotImplementedError

  def InsertFrenchDepartments(self, vals):
    raise NotImplementedError

class BackendError(Exception):
    pass
