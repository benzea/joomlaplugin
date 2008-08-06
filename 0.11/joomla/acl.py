import database

class JoomlaACL:
	def __init__(self, config):
		self._config = config
		self._min_aro_groups = self._config.aro_groups

	def login_allowed(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)

		if not gid:
			return False

		groups = self.get_parent_groups(id=gid)
		groups = groups.values()
		for group in self._min_aro_groups:
			if group in groups:
				return True
		return False

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
		
	def get_parent_groups(self, id=None, name=None):
		db = database.get_instance(self._config)
		cursor = db.cursor()
		
		table = db.table_name("core_acl_aro_groups")
		sql = """
		      SELECT child.group_id, child.name FROM %(table)s
		      parent LEFT JOIN %(table)s child ON parent.lft >= child.lft AND parent.rgt <= child.rgt
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
		if not gid:
			return {}

		return self.get_parent_groups(id=gid)

