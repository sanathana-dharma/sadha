from flask import current_app
from utils import get_client
from utils import from_datastore
from google.cloud import datastore

builtin_list = list
kind_name = 'Branch'

# [START list]
def list(branch_parent_id):
	ds = get_client()
	query = ds.query(kind=kind_name, order=['name'])
	if branch_parent_id != 0:
		#We have a valid parent # ID
		#This means we are loading children of a branch
		#print ("Fetching children of CategoryID")
		#print(branch_parent_id)
		query.add_filter('branch_parent_id', '=', branch_parent_id)
	else:
		#No parent branch id available
		#simply list root branches
		#print ("Fetching Root categories..")
		query.add_filter('branch_parent_id', '=', 0)

	entities = query.fetch(limit=10)
	return entities

# [END list]


def read(id):
    ds = get_client()
    key = ds.key(kind_name, int(id))
    rec = ds.get(key)
    return from_datastore(rec)


# [START update]
def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key(kind_name, int(id))
    else:
        key = ds.key(kind_name)
    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['description'])
    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update
# [END update]

def add(obj):
	ds = get_client()
	key = ds.key(kind_name)
	entity = datastore.Entity(key=key)
	data = {
		'id' : obj.id,
		'name' : obj.name,
		'branch_parent_id' : obj.branch_parent_id
	}
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)

def delete(id):
    ds = get_client()
    key = ds.key(kind_name, int(id))
    ds.delete(key)
