import re
from trac.core import *
from trac.config import *
from trac.web import IRequestHandler
from trac.web.api import IAuthenticator
from trac.web.chrome import INavigationContributor
from joomla.session import JoomlaSession
from joomla.acl import JoomlaACL
from joomla.config import IJoomlaConfig
from genshi.builder import tag

__all__ = ['JoomlaLoginModule']

class JoomlaLoginModule(Component):
	"""A module to integrate Trac with Joomla"""

	implements(IAuthenticator, INavigationContributor, IRequestHandler)

	configs = ExtensionPoint(IJoomlaConfig)

	def __init__(self):
		# Just use the first configuration provider
		self.config = self.configs[0]

	def authenticate(self, req):
		session = JoomlaSession(self.config, req)

		if session.get_username():
			acl = JoomlaACL(self.config)
			if acl.login_allowed(id=session.get_uid()):
				session.update_timestamp()
				return session.get_username()

		return None


	# INavigationContributor methods
	
	def get_active_navigation_item(self, req):
		return 'login'
	
	def get_navigation_items(self, req):
		if req.authname and req.authname != 'anonymous':
			yield ('metanav', 'login', 'logged in as %s' % req.authname)

			logout_url = self.config.logout_url
			if logout_url:
				yield ('metanav', 'logout', tag.a('Logout', href=logout_url))
		else:
			login_url = self.config.login_url
			if login_url:
				yield ('metanav', 'login', tag.a('Login', href=login_url))
	

	# IRequestHandler, this is just in case anything forwards to /login or /logout
	def match_request(self, req):
		return re.match('/(login|logout)/?$', req.path_info)

	def process_request(self, req):
		if req.path_info.startswith('/login'):
			if self.config.login_url:
				req.redirect(self.config.login_url)
			else:
				raise TracError(tag("You can only login on the Joomla installation."))

		if req.path_info.startswith('/logout'):
			if self.config.logout_url:
				req.redirect(self.config.logout_url)
			else:
				raise TracError(tag("You can only logout on the Joomla installation."))

		raise TracError(tag("Joomla plugin cannot handle requests that are not for /login or /logout. Something is broken!"))
		