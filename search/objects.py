from treemgr import model_datastore as treemgr_model_datastore
from contentmgr import model_datastore as contentmgr_model_datastore
from utils import Error
import config
from _private import keys
from utils import Error

#Search related imports
from _private import keys
import requests
from algoliasearch.search_client import SearchClient

#Elastic search
import certifi
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections, Search, Q
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Match, MultiMatch

# MODEL for tree
class Tree (Document):
	branch_id = Text()
	branch_name = Text()
	branch_parent_id = Text()
	sortorder = Integer()
	tags = Keyword()
	published_date = Date()

	class Index:
	    name = 'tree'
#	    settings = {
#	      "number_of_shards": 2,
#	    }

	def save(self, ** kwargs):
		return super(Tree, self).save(** kwargs)

	def is_published(self):
		return datetime.now() >= self.published_date

# MODEL for content
class Content(Document):
	leaf_id = Text()
	branch_id = Text()
	branch_name = Text()
	content_eng = Text()
	content_san = Text()
	content_kan = Text()
	master_branch_name = Text()
	content_type_name = Text()
	source_doc_name = Text()
	tags = Keyword()
	lines = Integer()
	published_date = Date()

	class Index:
	    name = 'content'
#	    settings = {
#	      "number_of_shards": 2,
#	    }

	def save(self, ** kwargs):
		try:
			self.lines = len(self.content_san.split())
		except:
			pass
		return super(Content, self).save(** kwargs)

	def is_published(self):
		return datetime.now() >= self.published_date

class clsElasticIndex:
	def __init__(self):
		#Create default connection
		connections.create_connection(
			hosts=[keys.ELASTICSEARCH_ENDPOINT_URL],
			timeout=20,
			http_auth=(keys.ELASTICSEARCH_USERNAME, keys.ELASTICSEARCH_PASSWORD),
			use_ssl=True,
			verify_certs=True,
			ca_certs=certifi.where()
			)


		#ES DSL method
		self.es_client = None
		try:
			self.es_client = Elasticsearch(
			  [keys.ELASTICSEARCH_CLUSTER_URL],
			  http_auth=(keys.ELASTICSEARCH_USERNAME, keys.ELASTICSEARCH_PASSWORD),
			  port=keys.ELASTICSEARCH_CLUSTER_PORT,
			  use_ssl=True,
			  verify_certs=True,
			  ca_certs=certifi.where())

			print ("clsElasticIndex.__init__: Connected to elastic server")
			#print(self.es_client)

		except Exception as ex:
		  print("Error:")
		  print(ex)

	def execute_query(self, index, query):
		#DSL Method
		s = Search(using=self.es_client, index=index)
		s = s.query(query)
		response = s.execute()

		print("clsElasticIndex.execute_query: response=")
		print(response.to_dict())
		return response.to_dict()

	def delete(self,index, id):
		#Query for the record
		if index=="content":
			s = Content.get(id=id)
		elif index=="tree":
			s = Tree.get(id)
		#Delete
		s.delete()
		return True


	def create_update_leaf(self, index, obj):
		# create the mappings in elasticsearch
		Content.init(index=index, using=self.es_client)

		# create and save and article
		content1 = Content(
				meta={'id': obj.leaf_id},
				leaf_id=obj.leaf_id,
				branch_id=obj.branch_id,
				branch_name=obj.branch_name,
				content_eng=obj.content_eng,
				content_san=obj.content_san,
				content_kan=obj.content_kan,
				master_branch_name=obj.master_branch_name,
				content_type_name=obj.content_type_name,
				source_doc_name=obj.source_doc_name,
				tags=['test1', 'test2'])
		content1.published_date = datetime.now()

		try:
			content1.save()
			if content1.is_published():
				return True
			raise Error("*** search.objects.create_update_leaf: Error! Unable to write leaf/content to Elastic.")
			return False
		except Exception as Ex:
			raise Error("*** search.objects.create_update_leaf: Exception occured! Unable to write leaf/content to Elastic.")
			print(Ex)
			return False

	def create_update_branch(self, index, obj):
		# create the mappings in elasticsearch
		Tree.init(index=index, using=self.es_client)

		# create and save and article
		tree1 = Tree(
				meta={'id': obj.id},
				branch_id=obj.id,
				branch_name=obj.name,
				branch_parent_id=obj.branch_parent_id,
				sortorder=obj.sortorder,
				tags=['test1', 'test2'])
		tree1.published_date = datetime.now()

		try:
			tree1.save()
			if tree1.is_published():
				return True
			raise Error("*** search.objects.create_update_branch: Error! Unable to write branch to Elastic.")
			return False
		except Exception as Ex:
			raise Error("*** search.objects.create_update_branch: Exception occured! Unable to write branch to Elastic.")
			print(Ex)
			return False


	# ===================================================================
	# Add data to index
	# We do all the splitting of data before this function is called
	# Here we simply save the data to index
	# ===================================================================
	def add_to_index(self, index_name, dict_data):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		lstDict_data = []
		lstDict_data.append(dict_data)
		#Save multiple objects
		resp = index.save_objects(lstDict_data, {'autoGenerateObjectIDIfNotExist': True})
		#Save single object
		#resp = index.save_object(dict_data)
		print("Add to index.. Done!")
		return resp

	# ===================================================================
	# Update data in index
	# We must update the existing object in index using objectID and update it
	# Here we assume that updating of a single record in our database requires
	# updating of only one single object in the index.
	# All code is same as ADD function. We have different functions here
	# for add and update data just as placeholders if we use a different
	# search service in future.
	# ===================================================================
	def update_data_in_index(self, index_name, dict_data):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		lstDict_data = []
		lstDict_data.append(dict_data)
		#Updating multiple objects in index
		resp = index.save_objects(lstDict_data, {'autoGenerateObjectIDIfNotExist': True})
		print("Update data in index.. Done!")
		return resp

	# ===================================================================
	# Delete specific records in index using query by objectID
	# When we split a long content record into smaller records for indexing,
	# We insert branch_id as contentID (For TREE index) in each record
	# So now using query we delete all those records when required
	# ===================================================================
	def delete_data_in_index(self, index_name, objectID):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		#Delete single object using objectID
		resp = index.delete_objects([objectID])
		#Delete multiple objects using query
		#index.delete_by({
		#  'filters': 'contentID:'+contentID
		#})
		print("Deleting data in index. Done!")
		return resp



	#Data format sent for indexing (for reference)
	#data = [
	#			{
	#				"title": 			"xxx",
	#				"permalink":		"http://abc",
	#				"content":			"content goes here"
	#			},
	#			{
	#				"title": 			"xxx",
	#				"permalink":		"http://abc",
	#				"content":			"content goes here"
	#			}
	#		]

	#Indexing Branches
	#	branch name
	#	path
	#	permalink
	#	contentID

	#Indexing Content
	#	ContentType: Source
	#	Source document: name
	#	Content_lang: upto 500 chars
	#	permalink_content
	#	permalink_source_document

class clsSearch_algolia:
	def __init__(self):
		pass

	# ===================================================================
	# Add data to index
	# We do all the splitting of data before this function is called
	# Here we simply save the data to index
	# ===================================================================
	def add_to_index(self, index_name, dict_data):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		lstDict_data = []
		lstDict_data.append(dict_data)
		#Save multiple objects
		resp = index.save_objects(lstDict_data, {'autoGenerateObjectIDIfNotExist': True})
		#Save single object
		#resp = index.save_object(dict_data)
		print("Add to index.. Done!")
		return resp

	# ===================================================================
	# Update data in index
	# We must update the existing object in index using objectID and update it
	# Here we assume that updating of a single record in our database requires
	# updating of only one single object in the index.
	# All code is same as ADD function. We have different functions here
	# for add and update data just as placeholders if we use a different
	# search service in future.
	# ===================================================================
	def update_data_in_index(self, index_name, dict_data):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		lstDict_data = []
		lstDict_data.append(dict_data)
		#Updating multiple objects in index
		resp = index.save_objects(lstDict_data, {'autoGenerateObjectIDIfNotExist': True})
		print("Update data in index.. Done!")
		return resp

	# ===================================================================
	# Delete specific records in index using query by objectID
	# When we split a long content record into smaller records for indexing,
	# We insert branch_id as contentID (For TREE index) in each record
	# So now using query we delete all those records when required
	# ===================================================================
	def delete_data_in_index(self, index_name, objectID):
		#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching
		client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for adding data to index
		index = client.init_index(config.DICT_SEARCH_INDEXES[index_name])

		#Delete single object using objectID
		resp = index.delete_objects([objectID])
		#Delete multiple objects using query
		#index.delete_by({
		#  'filters': 'contentID:'+contentID
		#})
		print("Deleting data in index. Done!")
		return resp
