import database

class JoomlaACL:
	def __init__(self, config):
		self._config = config
		self._min_aro_group = self._config.get("aro_group")

	def is_allowed(self, uid):
		gid = self.get_user_gid_by_uid(uid)
		
		lft = self.get_group_lft_by_id(gid)
		min_lft = self.get_group_lft_by_name(self._min_aro_group)

		return lft >= min_lft


	def get_user_gid_by_name(self, username):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		user_table = db.table_name("users")
		sql = "SELECT gid FROM %s WHERE username=%%s" % (user_table)
		cursor.execute(sql, username)

		if cursor.rowcount == 0:
			return 0

		gid = cursor.fetchone()[0]
		return gid

	def get_user_gid_by_uid(self, uid):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		user_table = db.table_name("users")
		sql = "SELECT gid FROM %s WHERE id=%%s" % (user_table)
		cursor.execute(sql, uid)

		if cursor.rowcount == 0:
			return 0

		gid = cursor.fetchone()[0]
		return gid

	def get_group_lft_by_name(self, group):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("core_acl_aro_groups")
		sql = "SELECT lft FROM %s WHERE name=%%s" % (table)
		cursor.execute(sql, group)

		if cursor.rowcount == 0:
			return 0

		return cursor.fetchone()[0]

	def get_group_lft_by_id(self, gid):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("core_acl_aro_groups")
		sql = "SELECT lft FROM %s WHERE group_id=%%s" % (table)
		cursor.execute(sql, gid)

		if cursor.rowcount == 0:
			return 0

		return cursor.fetchone()[0]


	def get_user_groups(self, username):
		gid = self.get_user_gid_by_name(username)
		lft = self.get_group_lft_by_id(gid)

		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("core_acl_aro_groups")
		sql = "SELECT name FROM %s WHERE lft<=%%s" % table
		cursor.execute(sql, lft)

		groups = []

		for row in cursor.fetchall():
			groups.append(row[0])

		return groups

