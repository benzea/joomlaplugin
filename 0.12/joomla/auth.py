import re
from trac.core import *
from trac.config import Option
from trac.web import IRequestHandler
from trac.web.api import IAuthenticator
from trac.web.chrome import INavigationContributor
from joomla.session import JoomlaSession
from joomla.acl import JoomlaACL
from joomla.database import JoomlaDatabaseManager
from genshi.builder import tag

__all__ = ['JoomlaLoginModule']

class JoomlaLoginModule(Component):
	"""A module to integrate Trac with Joomla"""

	implements(IAuthenticator, INavigationContributor, IRequestHandler)

	login_url = Option('joomla', 'login_url', None, 'Location that users are redirected if they press on the login button. If not set, no login link will appear.')
	logout_url = Option('joomla', 'logout_url', None, 'Location that users are redirected if they press on the logout button. If not set, no logout link will appear.')

	def __init__(self):
		pass

	def authenticate(self, req):
		session = JoomlaSession(self.env)
		user = session.get_user(req)

		if user:
			acl = JoomlaACL(self.env)
			if acl.login_allowed(id=user.uid):
				session.update_timestamp(user)
				session.update_userdata_from_joomla(user)
				return user.username

		return None


	# INavigationContributor methods
	
	def get_active_navigation_item(self, req):
		return 'login'
	
	def get_navigation_items(self, req):
		if req.authname and req.authname != 'anonymous':
			yield ('metanav', 'login', 'logged in as %s' % req.authname)

			logout_url = self.logout_url
			if logout_url:
				yield ('metanav', 'logout', tag.a('Logout', href=logout_url, target="_top"))
		else:
			login_url = self.login_url
			if login_url:
				yield ('metanav', 'login', tag.a('Login', href=login_url, target="_top"))
	

	# IRequestHandler, this is just in case anything forwards to /login or /logout
	def match_request(self, req):
		return re.match('/(login|logout)/?$', req.path_info)

	def process_request(self, req):
		if req.path_info.startswith('/login'):
			if self.login_url:
				req.redirect(self.login_url)
			else:
				raise TracError(tag("You can only login on the Joomla installation."))

		if req.path_info.startswith('/logout'):
			if self.logout_url:
				req.redirect(self.logout_url)
			else:
				raise TracError(tag("You can only logout on the Joomla installation."))

		raise TracError(tag("Joomla plugin cannot handle requests that are not for /login or /logout. Something is broken!"))
		
