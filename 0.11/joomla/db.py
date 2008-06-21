
import MySQLdb
import joomla_config as config

_connection = None

def table_name(table):
    return config.TABLE_PREFIX + table

def get_connection():
    global _connection
    if not _connection:
        _connection = MySQLdb.connect(user=config.MYSQL_USER, passwd=config.MYSQL_PASS, db=config.MYSQL_DB)
    
    return _connection
