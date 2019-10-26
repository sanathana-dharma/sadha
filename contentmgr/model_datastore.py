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
	query = ds.query(kind=kind_name)
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
def update(data, leaf_id):
	ds = get_client()
	key = ds.key(kind_name, int(leaf_id))
	entity = datastore.Entity(
	    key=key,
	    exclude_from_indexes=['content_eng', 'content_kan', 'content_san'])
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)
# [END update]

#Creates a new leaf
def add(obj):
	ds = get_client()
	key = ds.key(kind_name)
	entity = datastore.Entity(key=key)
	data = {
		'branch_id' : obj.branch_id,
		'content_eng' : obj.content_eng,
		'content_san' : obj.content_san,
		'content_kan' : obj.content_kan,
	}
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)

#Deletes a leaf
def delete(leaf_id):
    ds = get_client()
    key = ds.key(kind_name, int(leaf_id))
    ds.delete(key)
