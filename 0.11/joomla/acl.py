
import db

class ACL:
	def __init__(self, module):
		self._module = module

	def is_allowed(self, uid):
		conn = db.get_connection(self._module)
		cursor = conn.cursor()
		
		group_table = db.table_name(self._module, "core_acl_aro_groups")
		user_table = db.table_name(self._module, "users")
		sql = "SELECT gid FROM %s WHERE id=%%s" % (user_table)
		cursor.execute(sql, uid)

		if cursor.rowcount == 0:
			return False

		gid = cursor.fetchone()[0]
		
		lft = self.get_group_lft_by_id(gid)
		min_lft = self.get_group_lft_by_name(self._module.min_aro_group)
			
		return lft >= min_lft

	def get_group_lft_by_name(self, group):
		conn = db.get_connection(self._module)
		cursor = conn.cursor()
		
		table = db.table_name(self._module, "core_acl_aro_groups")
		sql = "SELECT lft FROM %s WHERE name=%%s" % (table)
		cursor.execute(sql, group)

		if cursor.rowcount == 0:
			return 0

		return cursor.fetchone()[0]

	def get_group_lft_by_id(self, gid):
		conn = db.get_connection(self._module)
		cursor = conn.cursor()
		
		table = db.table_name(self._module, "core_acl_aro_groups")
		sql = "SELECT lft FROM %s WHERE group_id=%%s" % (table)
		cursor.execute(sql, gid)

		if cursor.rowcount == 0:
			return 0

		return cursor.fetchone()[0]

