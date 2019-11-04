from flask import current_app
from utils import get_client
from utils import from_datastore
from google.cloud import datastore

builtin_list = list
kind_name = 'Branch'


def get_pagination_data(dataKind, cursor=None, pageSize=10):
    query = client.query(kind=dataKind)
    query_iter = query.fetch(start_cursor=cursor, limit=pageSize)
    page = next(query_iter.pages)

    entities = list(page)
    next_cursor = query_iter.next_page_token

    return entities, next_cursor

# [START list]
def list(branch_parent_id):
	ds = get_client()
	query = ds.query(kind=kind_name, order=['sortorder'])
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

	entities = query.fetch(limit=100)
	items = []
	count = 0
	for x in entities:
		count = count + 1
		items.append(x)
	#print("Listing branches. branch_parent_id=")
	#print(branch_parent_id)
	#print("Final count of branches=")
	#print(count)
	return items

# [END list]


def read(id):
    ds = get_client()
    key = ds.key(kind_name, int(id))
    rec = ds.get(key)
    return from_datastore(rec)

def get_next_sortorder(branch_parent_id):
	ds = get_client()
	query = ds.query(kind=kind_name, order=['-sortorder'])
	query.add_filter('branch_parent_id', '=', branch_parent_id)
	entities = query.fetch(limit=1)
	next_sortorder = 1
	for entity in entities:
		#Return the highest sortorder + 1
		next_sortorder = int(entity['sortorder']) + 1
	return next_sortorder

def get_next_record(branch_id, branch_parent_id):
	ds = get_client()
	query = ds.query(kind=kind_name, order=['sortorder'])
	#Fetch all siblings of this branch
	query.add_filter('branch_parent_id', '=', branch_parent_id)
	entities = query.fetch(limit=100)
	foundRecound = False
	count = 0
	print("Getting next branch details..")
	print("Total branches in this list=")
	for entity in entities:
		count = count + 1
		print(count)
		print(count)
		#first find the current record at hand
		print("entity.id=")
		print(entity.id)
		print("branch_id=")
		print(branch_id)
		if entity.id==branch_id:
			#We just found our current branch, next record is the one we are looking for
			print("We just found our current branch, next record is the one we are looking for ")
			foundRecound = True
		else:
			print("Not equal, moving to next loop")
			if foundRecound==True:
				print("This is the last loop, we will exit after we copy this last branch")
				next_branch = entity
				break
		print("For loop ended.")
		print("Next brach id =")
		print(next_branch.id)
	return next_branch


# [START update]
def update(obj):
	ds = get_client()
	key = ds.key(kind_name, obj.id)
	entity = datastore.Entity(key=key)
	data = {
		'name' : obj.name,
		'branch_parent_id' : obj.branch_parent_id,
		'sortorder': int(obj.sortorder)
	}
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)
# [END update]

def add(obj):
	ds = get_client()
	key = ds.key(kind_name)
	entity = datastore.Entity(key=key)
	data = {
		'name' : obj.name,
		'branch_parent_id' : obj.branch_parent_id,
		'sortorder': int(obj.sortorder)
	}
	entity.update(data)
	ds.put(entity)
	return from_datastore(entity)

def delete(obj):
    ds = get_client()
    key = ds.key(kind_name, int(obj.id))
    ds.delete(key)
