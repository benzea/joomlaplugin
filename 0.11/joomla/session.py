
import db
import sys
import md5
import joomla_config as config
import Cookie

class Session:
	def __init__(self, request):
		self._username = None
		self._guest = True
		self._uid = 0
		self._gid = 0
		self._usertype = None
		self._req = request

		self._load_from_cookie()
	
	def _load_from_cookie(self):
		conn = db.get_connection()
		cursor = conn.cursor()
		
		table = db.table_name("session")

		session_id = self._get_session_id()
		if not session_id:
			return

		sql = "SELECT username, guest, userid, usertype, gid FROM %s WHERE session_id=%%s AND time >= (UNIX_TIMESTAMP()-%i);" % (table, config.SESSION_LIFETIME)
		cursor.execute(sql, (session_id))
		if cursor.rowcount > 1:
			raise AssertionError

		if cursor.rowcount == 0:
			return

		row = cursor.fetchone()
		self._username = row[0]
		self._guest = row[1]
		self._uid = row[2]
		self._usertype = row[3]
		self._gid = row[4]

	def _get_session_id(self):
		cookie = self._get_cookie_value()
		if not cookie:
			return None

		hash = md5.md5()
		hash.update(cookie)
		hash.update(self._req.environ["REMOTE_ADDRESS"])
		hash.update(self._req.environ["HTTP_USER_AGENT"])

		session_hash = md5.md5()
		session_hash.update(config.HASH_SECRET)
		session_hash.update(hash.hexdigest())
	
		return session_hash.hexdigest()

	def _get_cookie_name(self):
		if self._req.environ["SERVER_NAME"].startswith("https://"):
			server_name = self._req.environ["SERVER_NAME"][8:]
		elif self._req.environ["SERVER_NAME"].startswith("http://"):
			server_name = self._req.environ["SERVER_NAME"][7:]
		else:
			server_name = config.LIVE_SITE

		hash = md5.md5("site" + server_name)
		return hash.hexdigest()

	def _get_cookie_value(self):
		cookie_name = self._get_cookie_name()

		if self._req.incookie.has_key(cookie_name):
			return self._req.incookie[cookie_name]
		else:
			return None
