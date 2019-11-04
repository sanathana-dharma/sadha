from contentmgr import model_datastore
import config

class clsLeaf:
	def __init__(self):
		self.leaf_id = None
		self.branch_id = None
		self.content_eng = ""
		self.content_san = ""
		self.content_kan = ""
		self.content_type_id = None
		self.source_doc_id = None
		self.branch_name = ""
		self.master_branch_name = ""

	def add(self,branch_id, content_type_id, source_doc_id):
		self.branch_id = branch_id
		self.content_type_id = content_type_id
		self.source_doc_id = source_doc_id
		model_datastore.add(self)

	def update(self,leaf_id, branch_id, content_type_id, source_doc_id):
		self.id = leaf_id
		self.branch_id = branch_id
		self.content_type_id = content_type_id
		self.source_doc_id = source_doc_id
		model_datastore.update(self)

	def populate_from_record(self,leaf):
		self.id = leaf.id
		self.branch_id = leaf['branch_id']
		self.content_eng = leaf['content_eng']
		self.content_san = leaf['content_san']
		self.content_kan = leaf['content_kan']
		self.content_type_id = leaf['content_type_id']
		self.source_doc_id = leaf['source_doc_id']
		self.content_type_name = config.DICT_CONTENT_TYPE[leaf['content_type_id']]
		self.source_doc_name = config.DICT_SOURCEDOCS[leaf['source_doc_id']]
