from trac.core import *
from trac.config import *

class IJoomlaConfig(Interface):
	def get(self, option):
		"""Return the configuration option."""

class JoomlaConfig(Component):
	session_lifetime = IntOption("joomla", "session_lifetime", default=2700, doc="The time until the session expires (in seconds).")
	hash_secret = Option("joomla", "hash_secret", default="", doc="The Secret that Joomla uses to salt its hashes.")
	live_site = Option("joomla", "live_site", default=None, doc="The Site to use for the cookie hash (defaults to the current hostname).")
	mysql_user = Option("joomla", "mysql_user", doc="The username to use to open the MySQL connection.")
	mysql_pass = Option("joomla", "mysql_pass", doc="The password to use to open the MySQL connection.")
	database = Option("joomla", "database", doc="The database to open.")
	table_prefix = Option("joomla", "table_prefix", doc="The table prefix to use.")
	aro_group = Option("joomla", "aro_group", doc="The minimum ARO Joomla Group that a user needs to have (will be downgraded to anonymous otherwise).")
	authz_file = Option('joomla', 'authz_file', None, 'Location of authz policy configuration file.')

	implements(IJoomlaConfig)
	
	def get(self, option):
		if option == "session_lifetime":
			return self.session_lifetime
		elif option == "hash_secret":
			return self.hash_secret
		elif option == "live_site":
			return self.live_site
		elif option == "mysql_user":
			return self.mysql_user
		elif option == "mysql_pass":
			return self.mysql_pass
		elif option == "database":
			return self.database
		elif option == "table_prefix":
			return self.table_prefix
		elif option == "aro_group":
			return self.aro_group
		elif option == "authz_file":
			return self.authz_file

		return None
