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
	aro_groups = ListOption("joomla", "aro_groups", doc="The minimum ARO Joomla Group that a user needs to have (will be downgraded to anonymous otherwise). This can be a list of allowed groups.")
	authz_file = Option('joomla', 'authz_file', None, 'Location of authz policy configuration file.')
	login_url = Option('joomla', 'login_url', None, 'Location that users are redirected if they press on the login button. If not set, no login link will appear.')
	logout_url = Option('joomla', 'logout_url', None, 'Location that users are redirected if they press on the logout button. If not set, no logout link will appear.')
	allow_anonymous = BoolOption('joomla', 'allow_anonymous', default=True, doc='If set to False, then users that are not authenticated in Trac will be redirected to the login_url.')

	implements(IJoomlaConfig)
