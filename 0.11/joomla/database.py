
from trac.core import *
from trac.config import *
import MySQLdb

class DB:
	def __init__(self, config):
		self._config = config
		self._connection = None
		
		self._mysql_user = self._config.mysql_user
		self._mysql_pass = self._config.mysql_pass
		self._mysql_db = self._config.database
		self._table_prefix = self._config.table_prefix

	def get_connection(self):
		if not self._connection:
			self._connection = MySQLdb.connect(user=self._mysql_user, passwd=self._mysql_pass, db=self._mysql_db)
	    
		return self._connection

	def table_name(self, table):
		return self._table_prefix + table

	def cursor(self):
		conn = self.get_connection()
		if conn:
			return conn.cursor()
		else:
			return None

_connections = {}
def get_instance(env):
	global _connections
	if not _connections.has_key(env):
		_connections[env] = DB(env)

	return _connections[env]
