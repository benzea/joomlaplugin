import database

class JoomlaACL:
	def __init__(self, config):
		self._config = config
		self._min_aro_group = self._config.get("aro_group")

	def login_allowed(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)

		groups = self.get_child_groups(name=self._min_aro_group)
		return groups.has_key(gid)

	def get_child_groups(self, id=None, name=None):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("core_acl_aro_groups")
		sql = """
		      SELECT child.group_id, child.name FROM %(table)s
		      parent LEFT JOIN %(table)s child ON parent.lft <= child.lft AND parent.rgt >= child.rgt
		      """ % { 'table': table}
		if id:
			sql += "WHERE parent.group_id = %s"
			param = str(id)
		elif name:
			sql += "WHERE parent.name = %s"
			param = name
		else:
			raise AssertionError

		cursor.execute(sql, param)

		result = {}
		for row in cursor.fetchall():
			result[row[0]] = row[1]
		return result
		

	def get_user_gid(self, id=None, name=None):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		user_table = db.table_name("users")
		if id:
			sql = "SELECT gid FROM %s WHERE id=%%s" % user_table
			param = id
		elif name:
			sql = "SELECT gid FROM %s WHERE username=%%s" % user_table
			param = name
		else:
			raise AssertionError

		cursor.execute(sql, param)

		if cursor.rowcount == 0:
			return None

		gid = cursor.fetchone()[0]

		return gid

	def get_user_groups(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)

		return self.get_child_groups(id=gid)

