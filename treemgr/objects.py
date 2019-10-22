class clsBranch:
	def __init__(self, id, name, branch_parent_id):
		try:
			self.id = id
		except:
			self.id = None
		self.name = name
		self.branch_parent_id = branch_parent_id
