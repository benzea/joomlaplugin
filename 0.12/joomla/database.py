from trac.db.api import DatabaseManager
from trac.config import Option


class JoomlaDatabaseManager(DatabaseManager):
	"""Class that provides access to the MySQL databse."""

	connection_uri = Option('joomla', 'database', None,
	                        'The Joomla Database that stores the session and user information.')
	table_prefix = Option("joomla", "table_prefix", doc="The table prefix to use.")

	def get_table_name(self, table):
		return self.table_prefix + table

