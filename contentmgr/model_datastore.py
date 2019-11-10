from flask import current_app
from utils import get_client
from utils import from_datastore
from google.cloud import datastore

builtin_list = list
kind_name = 'Content'

# [START list]
#Returns list of leaves under a single branch
def list_leaves(branch_id):
	ds = get_client()
	query = ds.query(kind=kind_name, order=['content_type_id'])
	query.add_filter('branch_id', '=', branch_id)
	entities = query.fetch(limit=10)
	return entities
# [END list]


#Returns details of a single leaf
def read_leaf(leaf_id):
    ds = get_client()
    key = ds.key(kind_name, int(leaf_id))
    rec = ds.get(key)
    return from_datastore(rec)

#Returns details of a single branch
def read_branch(branch_id):
    ds = get_client()
    key = ds.key('Branch', int(branch_id))
    rec = ds.get(key)
    return from_datastore(rec)

# [START update]
#Updates content of a single leaf
def update(obj):
	ds = get_client()
	key = ds.key(kind_name, int(obj.leaf_id))
	entity = datastore.Entity(
	    key=key,
	    exclude_from_indexes=['content_eng', 'content_kan', 'content_san'])
	data = {
		'branch_id' : obj.branch_id,
		'content_eng' : obj.content_eng,
		'content_san' : obj.content_san,
		'content_kan' : obj.content_kan,
		'content_type_id' : obj.content_type_id,
		'source_doc_id' : obj.source_doc_id
	}
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)
# [END update]

#Creates a new leaf
def create(obj):
	ds = get_client()
	key = ds.key(kind_name)
	entity = datastore.Entity(
		key=key,
		exclude_from_indexes=['content_eng', 'content_san', 'content_kan'])
	data = {
		'branch_id' : obj.branch_id,
		'content_eng' : obj.content_eng,
		'content_san' : obj.content_san,
		'content_kan' : obj.content_kan,
		'content_type_id' : obj.content_type_id,
		'source_doc_id' : obj.source_doc_id
	}
	entity.update(data)
	try:
		ds.put(entity)
		obj.leaf_id = entity.id
		return obj
	except Exception as Ex:
		raise Error("*** model_datastore.create: Error! Unable to write leaf/content to datastore.")
		print(Ex)
		return None

#Deletes a leaf
def delete(leaf_id):
    ds = get_client()
    key = ds.key(kind_name, int(leaf_id))
    ds.delete(key)
