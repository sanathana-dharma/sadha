from flask import current_app
from utils import get_client
from utils import from_datastore
from google.cloud import datastore

builtin_list = list


# [START list]
def list(branch_parent_id):
	ds = get_client()
	query = ds.query(kind='Branch', order=['name'])
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
	#print(entities)
	branch = {}
	branches = []
	return entities

# [END list]


def read(id):
    ds = get_client()
    key = ds.key('Branch', int(id))
    branch = ds.get(key)
    return from_datastore(branch)


# [START update]
def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('Branch', int(id))
    else:
        key = ds.key('Branch')
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
	key = ds.key('Branch')
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
    key = ds.key('Branch', int(id))
    ds.delete(key)
