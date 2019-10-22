from flask import current_app, Flask, redirect, render_template, request, url_for
from google.cloud import datastore
#from google.appengine.api import users

import config
builtin_list = list

def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'cloudsql':
        from . import model_cloudsql
        model = model_cloudsql
    elif model_backend == 'datastore':
        import treemgr.model_datastore
        model = treemgr.model_datastore
    elif model_backend == 'mongodb':
        from . import model_mongodb
        model = model_mongodb
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model


def get_client():
    return datastore.Client()


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.
    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]
    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()
    entity['id'] = entity.key.id
    return entity
# [END from_datastore]

# [Returns the full path of a branch from root as a list of branch IDs]
def get_tree_path(branch_id):
	item = {}
	path = []
	#print("Get tree path...")
	#print("branch_id=")
	#print(branch_id)
	x = 10
	#First time, check parent of current node
	branch_parent_id = branch_id
	while x > 0:
		ds = get_client()
		key = ds.key('Branch', int(branch_parent_id))
		e = ds.get(key)
		#print (e)
		item = {
			"id": e.id,
			"name": e['name']
		}
		#print("name="+e['name'])
		path.append(item.copy())
		item.clear()
		#print("branch_parent_id=")
		#print(branch_parent_id)
		branch_parent_id = e['branch_parent_id']
		#print (path)
		if branch_parent_id=='0':
			#print("branch_parent_id=0, breaking loop.")
			break
	#print ("Here is the final path:")
	#Reverse the items in the path
	path = path[::-1]
	return path

#Checks whether a given branch has children under it or not
#Returns a Boolean
def branch_has_children(branch_id):
	ds = get_client()
	query = ds.query(kind='Branch')
	query.add_filter('branch_parent_id', '=', branch_id)
	results = list(query.fetch(1))
	if len(results)>0:
		return True
	return False

#Returns list of languages enabled
def get_languagelist():
	#print("Languages configured:")
	#for x in config.LANGUAGES:
		#print(config.LANGUAGES[x])
	return config.LANGUAGES


def render_html(htmlFile, dictVariables):
	#Append variables for the template that are required globally for all views
	#Languages list
	languages = get_languagelist()
	dictVariables.update({"languages": languages})

	#Branch path
	if dictVariables['branch_parent_id']=='0':
		branch_path = []
	else:
		branch_path = get_tree_path(dictVariables['branch_parent_id'])
	dictVariables.update({"branch_path": branch_path})

	#User session
	#user = users.get_current_user()
	#if user:
	#    url = users.create_logout_url(self.request.uri)
	#    url_linktext = 'Logout'
	#else:
	#    url = users.create_login_url(self.request.uri)
	#    url_linktext = 'Login'
	#
	#dictVariables.update({
	#	"user": user,
	#    'url': url,
	#    'url_linktext': url_linktext,
	#})

	#Render template
	return render_template(htmlFile, **dictVariables)
