from trac.core import Component
from trac.config import Option, IntOption
from joomla.database import JoomlaDatabaseManager
import md5
import Cookie

class User(object):
	username = None
	guest = True
	uid = 0
	usertype = None
	session_id = None


class JoomlaSession(Component):
	session_lifetime = IntOption("joomla", "session_lifetime", default=15, doc="The time until the session expires (in minutes).")
	hash_secret = Option("joomla", "hash_secret", default="", doc="The Secret that Joomla uses to salt its hashes.")
	live_site = Option("joomla", "live_site", default=None, doc="The Site to use for the cookie hash (defaults to the current hostname).")
	session_name = Option("joomla", "session_name", default="site", doc="The session name to use (defaults to \"site\").")
	cookie_hash = Option("joomla", "cookie_hash", default=None, doc="Cookie hash override for the lazy, just copy the real value from the site (default: calculate using \"session_name\").")

	def get_user(self, req):
		user = self._get_user_from_session(req)
		if user is not None:
			return user

		return None

		# Try to create a joomla session from a "Remember Me" cookie
		#return self._create_session_from_remember_me(req)

	def update_timestamp(self, user):
		if user is None:
			return

		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		table = db.get_table_name("session")

		sql = "UPDATE %s SET time=UNIX_TIMESTAMP() WHERE session_id=%%s" % (table)
		cursor.execute(sql, (user.session_id,))
		cnx.commit()
		cnx.close()

	def update_userdata_from_joomla(self, user):
		if user is None:
			return

		# Get email and name from the Joomla! database
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		table = db.get_table_name("users")

		sql = "SELECT name,email FROM %s WHERE id=%%s" % (table)
		cursor.execute(sql, (user.uid,))

		if cursor.rowcount > 1:
			cnx.close()
			raise AssertionError

		if cursor.rowcount == 0:
			cnx.close()
			return None

		cnx.close()

		row = cursor.fetchone()
		data = {
			'name'  : row[0],
			'email' : row[1]
		}

		db = self.env.get_db_cnx()
		cursor = db.cursor()

		attrs = [(user.username, name) for name in ['email', 'name']]
		cursor.executemany("DELETE FROM session_attribute WHERE sid=%s AND name=%s", attrs)

		attrs = [(user.username, 1, k, v) for k, v in data.iteritems()]
		cursor.executemany("INSERT INTO session_attribute "
                                   "(sid,authenticated,name,value) "
                                   "VALUES(%s,%s,%s,%s)", attrs)
		
		db.commit()

	def _get_session_id(self, req):
		cookie = self._get_cookie_value(req)

		return cookie

	def _get_cookie_name(self, req):
		if self.cookie_hash is not None:
			return self.cookie_hash

		if not self.live_site:
			server_name = req.environ["HTTP_HOST"]
		else:
			server_name = self.live_site

		session_name = self.session_name
		name = md5.md5(self.hash_secret + session_name)
		name = name.hexdigest()

		# And hash again ...
		hash = md5.md5(name)

		return hash.hexdigest()

	def _get_cookie_value(self, req):
		cookie_name = self._get_cookie_name(req)

		if req.incookie.has_key(cookie_name):
			return req.incookie[cookie_name].value
		else:
			return None

	def _get_user_from_session(self, req):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		table = db.get_table_name("session")

		session_id = self._get_session_id(req)
		if not session_id:
			return None

		sql = "SELECT username, guest, userid, usertype FROM %s WHERE session_id=%%s AND guest=0 AND time >= (UNIX_TIMESTAMP()-%i);" \
		       % (table, self.session_lifetime * 60)
		cursor.execute(sql, (session_id))
		if cursor.rowcount > 1:
			cnx.close()
			raise AssertionError

		if cursor.rowcount == 0:
			cnx.close()
			return None

		user = User()

		row = cursor.fetchone()
		user.username = row[0]
		user.guest = row[1]
		user.uid = row[2]
		user.usertype = row[3]
		user.session_id = session_id

		cnx.close()
		
		return user

#	def _get_remember_me_cookie_name(self, req):
#		if not self.live_site:
#			server_name = req.environ["HTTP_HOST"]
#		else:
#			server_name = self.live_site

#		hash = md5.md5()
#		hash.update("remembermecookieusername")
#		hash.update(self._get_cookie_name(req))

#		name_hash = md5.md5()
#		name_hash.update(self.hash_secret)
#		name_hash.update(hash.hexdigest())

#		return name_hash.hexdigest()

#	def _get_remember_me_cookie_value(self, req):
#		cookie_name = self._get_remember_me_cookie_name(req)

#		if req.incookie.has_key(cookie_name):
#			return req.incookie[cookie_name].value
#		else:
#			return None

#	def _create_session_from_remember_me(self, req):
#		db = JoomlaDatabaseManager(self.env)
#		cnx = db.get_connection()
#		cursor = cnx.cursor()

#		cookie = self._get_remember_me_cookie_value(req)
#		if cookie is None:
#			return None

#		# Cookie is too short
#		if len(cookie) < 65:
#			return None

#		cookie_userhash = cookie[0:32]
#		cookie_passhash = cookie[32:64]
#		cookie_uid = cookie[64:]


#		table = db.get_table_name("users")

#		sql = "SELECT id, username, password, usertype FROM %s WHERE id=%%s AND block=0;" \
#		       % (table,)
#		cursor.execute(sql, (cookie_uid,))

#		if cursor.rowcount > 1:
#			cnx.close()
#			raise AssertionError

#		if cursor.rowcount == 0:
#			cnx.close()
#			return None

#		user = User()

#		row = cursor.fetchone()
#		user.guest = 0
#		user.uid = row[0]
#		user.username = row[1]
#		passwd = row[2]
#		user.usertype = row[3]

#		cnx.close()

#		hash = md5.md5()
#		hash.update(req.environ["HTTP_USER_AGENT"])

#		salt = md5.md5()
#		salt.update(self.hash_secret)
#		salt.update(hash.hexdigest())
#		salt = salt.hexdigest()

#		userhash = md5.md5()
#		userhash.update(user.username)
#		userhash.update(salt)
#		userhash = userhash.hexdigest()

#		passwd = passwd.split(':')[0]
#		passhash = md5.md5()
#		passhash.update(passwd)
#		passhash.update(salt)
#		passhash = passhash.hexdigest()

#		# XXX: Just check that everything is valid, do NOT create a Joomla session!
#		if userhash == cookie_userhash and passhash == cookie_passhash:
#			return user
#		else:
#			return None

