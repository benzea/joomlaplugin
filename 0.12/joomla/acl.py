from trac.core import Component
from trac.config import ListOption
from joomla.database import JoomlaDatabaseManager

class JoomlaACL(Component):
	login_groups = ListOption("joomla", "groups", default=['ROOT'], doc="The minimum Joomla group that a user needs to have (will be downgraded to anonymous otherwise). This can be a list of allowed groups.")

	def login_allowed(self, id=None, name=None):
		groups = self.get_user_groups(id=id, name=name)

		if groups.isdisjoint(self.login_groups):
			return False
		else:
			return True

	def get_user_groups(self, id=None, name=None):
		db = JoomlaDatabaseManager(self.env)
		cnx = db.get_connection()
		cursor = cnx.cursor()
		
		tables = dict()
		tables['users'] = db.get_table_name("users")
		tables['user_group_map'] = db.get_table_name("user_usergroup_map")
		tables['usergroups'] = db.get_table_name("usergroups")
		if id:
			sql = """SELECT DISTINCT child.id,child.title FROM %(user_group_map)s AS user_group_map
			            LEFT JOIN %(usergroups)s AS parent ON user_group_map.group_id=parent.id
			            LEFT JOIN %(usergroups)s AS child ON parent.lft >= child.lft AND parent.rgt <= child.rgt
			         WHERE user_group_map.user_id=%%s""" % tables
			param = id
		elif name:
			sql = """SELECT DISTINCT child.id,child.title FROM %(users)s as user
			            LEFT JOIN %(user_group_map)s AS user_group_map ON user.id=user_group_map.user_id
			            LEFT JOIN %(usergroups)s AS parent ON user_group_map.group_id=parent.id
			            LEFT JOIN %(usergroups)s AS child ON parent.lft >= child.lft AND parent.rgt <= child.rgt
			         WHERE user.username=%%s""" % tables
			param = name
		else:
			raise AssertionError

		cursor.execute(sql, param)

		if cursor.rowcount == 0:
			cnx.close()
			return None

		groups = set()
		for gid, groupname in cursor:
			groups.add(groupname)

		cnx.close()

		return groups


