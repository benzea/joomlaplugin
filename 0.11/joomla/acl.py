from trac.core import Component
from trac.config import ListOption
from joomla.database import JoomlaDatabaseManager

class JoomlaACL(Component):
	aro_groups = ListOption("joomla", "aro_groups", default=['ROOT'], doc="The minimum ARO Joomla Group that a user needs to have (will be downgraded to anonymous otherwise). This can be a list of allowed groups.")

	def login_allowed(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)

		if not gid:
			return False

		groups = self.get_parent_groups(id=gid)
		groups = groups.values()
		for group in self.aro_groups:
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
		
		table = db.get_table_name("core_acl_aro_groups")
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
			cnx.close()
			raise AssertionError

		cursor.execute(sql, param)

		result = {}
		for row in cursor.fetchall():
			result[row[0]] = row[1]

		cnx.close()

		return result

	def get_user_gid(self, id=None, name=None):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		user_table = db.get_table_name("users")
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
			cnx.close()
			return None

		gid = cursor.fetchone()[0]

		cnx.close()

		return gid

	def get_user_groups(self, id=None, name=None):
		gid = self.get_user_gid(id=id, name=name)
		if not gid:
			print "Could not get users GID"
			return {}

		print self.get_parent_groups(id=gid)
		return self.get_parent_groups(id=gid)

