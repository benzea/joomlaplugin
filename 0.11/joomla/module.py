from trac.core import *
from trac.config import *
from trac.web.api import IAuthenticator
from joomla.session import Session
from joomla.acl import ACL
import sys

__all__ = ['JoomlaModule']

class JoomlaModule(Component):
	"""A module to integrate Trac with Joomla"""
	mysql_user = Option("joomla", "mysql_user", doc="The username to use to open the MySQL connection.")
	mysql_pass = Option("joomla", "mysql_pass", doc="The password to use to open the MySQL connection.")
	mysql_db = Option("joomla", "database", doc="The database to open.")
	table_prefix = Option("joomla", "table_prefix", doc="The table prefix to use.")
	session_lifetime = IntOption("joomla", "session_lifetime", default=2700, doc="The time until the session expires (in seconds).")
	hash_secret = Option("joomla", "hash_secret", default="", doc="The Secret that Joomla uses to salt its hashes.")
	live_site = Option("joomla", "live_site", default=None, doc="The Site to use for the cookie hash (defaults to the current hostname).")

	min_aro_group = Option("joomla", "aro_group", doc="The minimum ARO Joomla Group that a user needs to have (will be downgraded to anonymous otherwise).")

	implements(IAuthenticator)

	def authenticate(self, req):
		session = Session(self, req)

		if session.get_username():
			acl = ACL(self)
			if acl.is_allowed(session.get_uid()):
				session.update_timestamp()
			else:
				return None
		
		return session._username

