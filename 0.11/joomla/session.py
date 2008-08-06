
import database
import md5
import Cookie


class JoomlaSession:
	#implements(IJoomlaSession)
	
	def __init__(self, config, req):
		self._username = None
		self._guest = True
		self._uid = 0
		self._gid = 0
		self._usertype = None
		self._session_id = None

		self._config = config
		self._req = req

		self._session_lifetime = self._config.session_lifetime
		self._hash_secret = self._config.hash_secret
		self._live_site = self._config.live_site

		self._load()
	
	def _load(self):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("session")

		session_id = self._get_session_id()
		if not session_id:
			return

		sql = "SELECT username, guest, userid, usertype, gid FROM %s WHERE session_id=%%s AND time >= (UNIX_TIMESTAMP()-%i);" \
		       % (table, self._session_lifetime)
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

	def update_timestamp(self):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("session")

		session_id = self._get_session_id()
		if not session_id:
			return

		sql = "UPDATE %s SET time=UNIX_TIMESTAMP() WHERE session_id=%%s" % (table)
		cursor.execute(sql, (session_id))
		# MySQL doesn't know about committing?


	def get_username(self):
		return self._username

	def get_uid(self):
		return self._uid

	def _get_session_id(self):
		if self._session_id:
			return self._session_id

		cookie = self._get_cookie_value()
		if not cookie:
			return None

		hash = md5.md5()
		hash.update(cookie)
		hash.update(self._req.environ["REMOTE_ADDR"])
		hash.update(self._req.environ["HTTP_USER_AGENT"])

		session_hash = md5.md5()
		session_hash.update(self._hash_secret)
		session_hash.update(hash.hexdigest())

		self._session_id = session_hash.hexdigest()
		return self._session_id

	def _get_cookie_name(self):
		if not self._live_site:
			server_name = self._req.environ["HTTP_HOST"]
		else:
			server_name = self._live_site

		hash = md5.md5("site" + server_name)
		return hash.hexdigest()

	def _get_cookie_value(self):
		cookie_name = self._get_cookie_name()

		if self._req.incookie.has_key(cookie_name):
			return self._req.incookie[cookie_name].value
		else:
			return None

