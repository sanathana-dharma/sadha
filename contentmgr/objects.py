from contentmgr import model_datastore
from search import objects as search_objects
import config
from contentmgr import objects as contentmgr_objects
from treemgr import objects as treemgr_objects
from search import objects as search_objects
from utils import Error
import utils
from _private import keys

#Elastic search
import certifi
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections, Search, Q
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Match, MultiMatch

LEAF_INDEX_NAME = 'content'

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

	def create (self):
		o = treemgr_objects.clsBranch()
		branch = o.read(self.branch_id)

		#Compute additional parameters before saving
		self.content_type_name = config.DICT_CONTENT_TYPE[self.content_type_id]
		self.source_doc_name = config.DICT_SOURCEDOCS[self.source_doc_id]
		self.branch_name = branch.name
		self.master_branch_name = utils.get_master_branch_name(self.branch_id)

		try:
			#Save to datastore
			savedobj = model_datastore.create(self)
			if savedobj:
				#==============================
				# The following line is very important
				# We use the object ID from datastore for saving in ES
				# for future retrival
				#==============================
				self.leaf_id = savedobj.leaf_id
				print("Saved to Datastore!")
			else:
				print("Saving to Datastore failed!")

			#Save to elasticsearch
			esobj = search_objects.clsElasticIndex()
			if esobj.create_update_leaf('content',self):
				print("Saved to Elastic!")
				return True
			else:
				print("Saving to Elastic failed!")
				return False
		except Exception as Ex:
			print("Exception: Saving to Elastic failed!")
			print(Ex)
			return False

	def update(self):
		o = treemgr_objects.clsBranch()
		branch = o.read(self.branch_id)

		#Compute additional parameters before saving
		self.content_type_name = config.DICT_CONTENT_TYPE[self.content_type_id]
		self.source_doc_name = config.DICT_SOURCEDOCS[self.source_doc_id]
		self.branch_name = branch.name
		self.master_branch_name = utils.get_master_branch_name(self.branch_id)

		try:
			#Save to datastore
			if model_datastore.update(self):
				print("Updated in Datastore!")
			else:
				print("Updating in Datastore failed!")

			#Save to elasticsearch
			esobj = search_objects.clsElasticIndex()
			if esobj.create_update_leaf('content',self):
				print("Saved to Elastic!")
				return True
			else:
				print("Saving to Elastic failed!")
				return False
		except Exception as Ex:
			print("Exception: Saving to Elastic failed!")
			print(Ex)
			return False

	def delete(self, leaf_id):
		print("Deleting leaf ID:")
		print(leaf_id)

		#Delete from datastore
		model_datastore.delete(leaf_id)
		print("Deleted leaf from Datastore!")

		#Delete from Elasticsearch
		o = search_objects.clsElasticIndex()
		'''
		query = {
				  "query": {
				    "match": {
				      "_id": {
				        "query": leaf_id,
				        "type": "phrase"
				      }
				    }
				  }
				}

		es = Elasticsearch(
		  [keys.ELASTICSEARCH_CLUSTER_URL],
		  http_auth=(keys.ELASTICSEARCH_USERNAME, keys.ELASTICSEARCH_PASSWORD),
		  port=keys.ELASTICSEARCH_CLUSTER_PORT,
		  use_ssl=True,
		  verify_certs=True,
		  ca_certs=certifi.where())
'''
		#resp = es.delete(index=LEAF_INDEX_NAME, id=leaf_id)
		#print (resp)


		#query = Q("match": {"_id": {"query": leaf_id, "type": "phrase"}})
		o.delete(LEAF_INDEX_NAME, leaf_id)
		print("Deleted leaf from ES!")

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
