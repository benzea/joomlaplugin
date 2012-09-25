from trac.core import Component
from trac.config import ListOption
from joomla.database import JoomlaDatabaseManager

class JoomlaACL(Component):
	login_groups = ListOption("joomla", "groups", default=['ROOT'], doc="The minimum Joomla group that a user needs to have (will be downgraded to anonymous otherwise). This can be a list of allowed groups.")

	def login_allowed(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)

		if not gid:
			return False

		groups = self.get_parent_groups(id=gid)
		groups = groups.values()
		for group in self.login_groups:
			if group in groups:
				return True
		return False

	def get_child_groups(self, id=None, name=None):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		table = cnx.get_table_name("core_acl_aro_groups")
		sql = """
		      SELECT child.group_id, child.name FROM %(table)s
		      parent LEFT JOIN %(table)s child ON parent.lft <= child.lft AND parent.rgt >= child.rgt
		      """ % { 'table': table }
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

		cnx.close()

		return result
		
	def get_parent_groups(self, id=None, name=None):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()

		table = db.get_table_name("usergroups")
		sql = """
		      SELECT child.id, child.title FROM %(table)s
		      parent LEFT JOIN %(table)s child ON parent.lft >= child.lft AND parent.rgt <= child.rgt
		      """ % { 'table': table}
		if id:
			sql += "WHERE parent.id = %s"
			param = str(id)
		elif name:
			sql += "WHERE parent.title = %s"
			param = name
		else:
			cnx.close()
			raise AssertionError

		cursor.execute(sql, param)

		result = {}
		for row in cursor.fetchall():
			result[row[0]] = row[1]

		cnx.close()

		return result

	def get_user_group(self, id=None, name=None):
		"""Why do people put strings into the columns? I just don't understand
		things like that ..."""
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		tables = dict()
		tables['users'] = db.get_table_name("users")
		tables['usergroups'] = db.get_table_name("usergroups")
		if id:
			sql = "SELECT %(usergroups)s.id, %(users)s.usertype FROM %(users)s LEFT JOIN %(usergroups)s ON %(users)s.usertype=%(usergroups)s.title WHERE %(users)s.id=%%s" % tables
			param = id
		elif name:
			sql = "SELECT %(usergroups)s.id, %(users)s.usertype FROM %(users)s LEFT JOIN %(usergroups)s ON %(users)s.usertype=%(usergroups)s.title WHERE %(users)s.username=%%s" % tables
			param = name
		else:
			raise AssertionError

		cursor.execute(sql, param)

		if cursor.rowcount == 0:
			cnx.close()
			return None

		gid, groupname = cursor.fetchone()

		cnx.close()

		return gid, groupname

	def get_user_gid(self, id=None, name=None):
		res = self.get_user_group(id, name)
		if res != None:
			return res[0]
		else:
			return None

	def get_user_group_name(self, id=None, name=None):
		res = self.get_user_group(id, name)
		if res != None:
			return res[1]
		else:
			return None

	def get_user_groups(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)
		if not gid:
			return {}

		return self.get_parent_groups(id=gid)

