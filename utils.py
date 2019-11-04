from flask import current_app, Flask, redirect, render_template, request, url_for, Markup
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from google.cloud import datastore
#from google.appengine.api import users

from _private import keys
import config
builtin_list = list

class Error(Exception):
	def __init__(self, message):
		self.message = message
		print(message)
	def __str__(self):
		return repr(self.message)

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
	lstpath = []
	#print("Get tree path...")
	#print("branch_id=")
	#print(branch_id)
	x = 10
	#First time, check parent of current node
	branch_parent_id = branch_id
	isRootBranch = False
	while x > 0:
		ds = get_client()
		try:
			key = ds.key('Branch', int(branch_parent_id))
			e = ds.get(key)
			#print (e)
			item = {
				"id": e.id,
				"name": e['name']
			}
			#print("name="+e['name'])
			lstpath.append(item.copy())
			item.clear()
			#print("branch_parent_id=")
			#print(branch_parent_id)
			branch_parent_id = e['branch_parent_id']
			#print (path)
			if branch_parent_id=='0':
				#print("branch_parent_id=0, breaking loop.")
				break
		except:
			isRootBranch = True
			break

	#print ("Here is the final path:")
	#Reverse the items in the path
	if isRootBranch:
		return "Home"
	else:
		lstpath = lstpath[::-1]
		return lstpath

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
	return config.DICT_LANGUAGES


def remove_html_tags(text):
	"""Remove html tags from a string"""
	#print(text)
	#First replace linebreaks to something NON-HTML so that it wont be cleared in the next step.
	text = text.replace("<br>", "BRBRBR")
	#print(text)

	import re
	clean = re.compile('<.*?>')
	clean  = re.sub(clean, '', text)
	#print(clean)
	#Again replace back our linebreaks to HTML format
	clean = clean.replace("BRBRBR", "<br>")
	#print(clean)
	#print("---end---")
	return Markup(clean)



#Validates if the current logged in user is authorized to access the given url
#and do appropriate redirect
def redirect_admin_only():
	if current_user.is_authenticated:
		if current_user.email in keys.ADMIN_LIST:
			return redirect("/admin")
		else:
			return "Sorry! unauthorized user. <a href='/logout'>Login as a different user</a>"

	else:
		return render_template("index.html")

def render_html(htmlFile, dictVariables):
	#Append variables for the template that are required globally for all views

	if current_user.is_authenticated:
		dictVariables.update({"name": current_user.name})
		dictVariables.update({"email": current_user.email})
		dictVariables.update({"profile_pic": current_user.profile_pic})
	else:
		pass

	#Languages list
	languages = get_languagelist()
	dictVariables.update({"languages": languages})

	#Content Type
	dictVariables.update({"content_type": config.DICT_CONTENT_TYPE})


	#Source docs
	dictVariables.update({"source_docs": config.DICT_SOURCEDOCS})

	#Branch path
	try:
		if dictVariables['branch_parent_id']=='0':
			branch_path = []
		else:
			branch_path = get_tree_path(dictVariables['branch_parent_id'])
		dictVariables.update({"branch_path": branch_path})
	except:
		pass


	#Render template
	return render_template(htmlFile, **dictVariables)
