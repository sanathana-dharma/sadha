class clsLeaf:
	def __init__(self, id, branch_id):
		try:
			self.id = id
		except:
			self.id = None
		self.branch_id = branch_id
		self.content_eng = ""
		self.content_san = ""
		self.content_kan = ""
