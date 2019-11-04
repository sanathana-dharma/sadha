from treemgr import model_datastore as treemgr_model_datastore
from contentmgr import model_datastore as contentmgr_model_datastore
from utils import Error
import config

#Search related imports
from _private import keys
import requests
from algoliasearch.search_client import SearchClient

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


class clsSearch:
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
