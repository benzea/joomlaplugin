from trac.core import *
from trac.config import *
from trac.web.api import IAuthenticator
from joomla.session import JoomlaSession
from joomla.acl import JoomlaACL
from joomla.config import IJoomlaConfig

__all__ = ['JoomlaModule']

class JoomlaAuthenticator(Component):
	"""A module to integrate Trac with Joomla"""

	implements(IAuthenticator)

	configs = ExtensionPoint(IJoomlaConfig)

	def __init__(self):
		# Just use the first configuration provider
		self.config = self.configs[0]

	def authenticate(self, req):
		session = JoomlaSession(self.config, req)

		if session.get_username():
			acl = JoomlaACL(self.config)
			if acl.is_allowed(session.get_uid()):
				session.update_timestamp()
			else:
				return None
		
		return session._username

