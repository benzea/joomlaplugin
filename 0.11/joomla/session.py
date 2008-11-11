from trac.core import Component
from trac.config import Option, IntOption
from joomla.database import JoomlaDatabaseManager
import md5
import Cookie

class User(object):
	username = None
	guest = True
	uid = 0
	gid = 0
	usertype = None
	session_id = None


class JoomlaSession(Component):
	session_lifetime = IntOption("joomla", "session_lifetime", default=2700, doc="The time until the session expires (in seconds).")
	hash_secret = Option("joomla", "hash_secret", default="", doc="The Secret that Joomla uses to salt its hashes.")
	live_site = Option("joomla", "live_site", default=None, doc="The Site to use for the cookie hash (defaults to the current hostname).")

	def get_user(self, req):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		table = db.get_table_name("session")

		session_id = self._get_session_id(req)
		if not session_id:
			return None

		sql = "SELECT username, guest, userid, usertype, gid FROM %s WHERE session_id=%%s AND guest=0 AND time >= (UNIX_TIMESTAMP()-%i);" \
		       % (table, self.session_lifetime)
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
		user.gid = row[4]
		user.session_id = session_id

		cnx.close()
		
		return user

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

		cursor.execute("DELETE FROM session_attribute WHERE sid=%s", (user.username, ))

		attrs = [(user.username, 1, k, v) for k, v in data.iteritems()]
		cursor.executemany("INSERT INTO session_attribute "
                                   "(sid,authenticated,name,value) "
                                   "VALUES(%s,%s,%s,%s)", attrs)
		
		db.commit()

	def _get_session_id(self, req):
		cookie = self._get_cookie_value(req)
		if not cookie:
			return None

		hash = md5.md5()
		hash.update(cookie)
		hash.update(req.environ["REMOTE_ADDR"])
		hash.update(req.environ["HTTP_USER_AGENT"])

		session_hash = md5.md5()
		session_hash.update(self.hash_secret)
		session_hash.update(hash.hexdigest())

		return session_hash.hexdigest()

	def _get_cookie_name(self, req):
		if not self.live_site:
			server_name = req.environ["HTTP_HOST"]
		else:
			server_name = self.live_site

		hash = md5.md5("site" + server_name)
		return hash.hexdigest()

	def _get_cookie_value(self, req):
		cookie_name = self._get_cookie_name(req)

		if req.incookie.has_key(cookie_name):
			return req.incookie[cookie_name].value
		else:
			return None

