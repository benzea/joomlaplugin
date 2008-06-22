
import MySQLdb

_connection = None

def table_name(module, table):
    return module.table_prefix + table

def get_connection(module):
    global _connection
    if not _connection:
        _connection = MySQLdb.connect(user=module.mysql_user, passwd=module.mysql_pass, db=module.mysql_db)
    
    return _connection
