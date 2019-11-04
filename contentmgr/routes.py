from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import utils
import config
from contentmgr import objects
from contentmgr import model_datastore

#Register as Blueprint module
mod3 = Blueprint('contentmgr', __name__, template_folder='templates')


# ========================================================
# LIST LEAVES (UNDER A BRANCH)
# ========================================================
@mod3.route('/view/<branch_id>')
@login_required
def list_leaves(branch_id):
		#```````````````````````````````````````````````````````````
		# GET METHOD
		#```````````````````````````````````````````````````````````
		#print("Inside content mgr view...")
		leaves = model_datastore.list_leaves(branch_id)
		branch = model_datastore.read_branch(branch_id)
		#Read and print each leaf with all its parameters
		di = {}
		lstleaves = []

		for content in leaves:
			obj = objects.clsLeaf()
			obj.id = content.id
			obj.branch_id = content['branch_id']
			obj.content_type_id = content['content_type_id']
			obj.source_doc_id = content['source_doc_id']
			if content['content_eng']:
				obj.content_eng = utils.remove_html_tags(content['content_eng'])
			if content['content_san']:
				obj.content_san = utils.remove_html_tags(content['content_san'])
			if content['content_kan']:
				obj.content_kan = utils.remove_html_tags(content['content_kan'])
			obj.content_type_name = config.DICT_CONTENT_TYPE[content['content_type_id']]
			obj.source_doc_name = config.DICT_SOURCEDOCS[content['source_doc_id']]
			#Add to list
			lstleaves.append(obj)
			del obj

		#Send output
		di = {
		"lstleaves": lstleaves,
		"catname": branch['name'],
		"branch_id": branch_id,
		"branch_parent_id": branch['branch_parent_id']
		}
		return utils.render_html("contentmgr-list.html",di)

# ========================================================
# LIST LEAVES (UNDER A BRANCH) - INTO A DIV
# ========================================================
@mod3.route('/view-div/<branch_id>')
@login_required
def list_leaves_div(branch_id):
		#```````````````````````````````````````````````````````````
		# GET METHOD
		#```````````````````````````````````````````````````````````
		#print("Inside content mgr view...")
		leaves = model_datastore.list_leaves(branch_id)
		branch = model_datastore.read_branch(branch_id)
		#Read and print each leaf with all its parameters
		di = {}
		lstleaves = []

		for content in leaves:
			obj = objects.clsLeaf()
			obj.id = content.id
			obj.branch_id = content['branch_id']
			obj.content_type_id = content['content_type_id']
			obj.source_doc_id = content['source_doc_id']
			if content['content_eng']:
				obj.content_eng = utils.remove_html_tags(content['content_eng'])
			if content['content_san']:
				obj.content_san = utils.remove_html_tags(content['content_san'])
			if content['content_kan']:
				obj.content_kan = utils.remove_html_tags(content['content_kan'])
			obj.content_type_name = config.DICT_CONTENT_TYPE[content['content_type_id']]
			obj.source_doc_name = config.DICT_SOURCEDOCS[content['source_doc_id']]
			#Add to list
			lstleaves.append(obj)
			del obj

		#Send output
		di = {
		"lstleaves": lstleaves,
		"catname": branch['name'],
		"branch_id": branch_id,
		"branch_parent_id": branch['branch_parent_id']
		}

		return utils.render_template("contentmgr-list-div.html",
		lstleaves =  lstleaves,
		catname =  branch['name'],
		branch_id = branch_id,
		branch_parent_id = branch['branch_parent_id']
		)

# ========================================================
# ADD LEAF (UNDER A BRANCH)
# ========================================================
@mod3.route('/add/<branch_id>', methods=['GET', 'POST'])
@login_required
def add(branch_id):
	#```````````````````````````````````````````````````````````
	# POST METHOD
	#```````````````````````````````````````````````````````````
	if request.method == 'POST':
		#Fetch content being added
		content_eng = request.form['content_eng']
		content_san = request.form['content_san']
		content_kan = request.form['content_kan']
		content_type_id = request.form['content_type_id']
		source_doc_id = request.form['source_doc_id']

		obj = objects.clsLeaf()
		obj.branch_id = branch_id
		obj.content_type_id = content_type_id
		obj.source_doc_id = source_doc_id

		if content_eng=="<div><br></div>":
			obj.content_eng = ""
		else:
			obj.content_eng = content_eng

		if content_san=="<div><br></div>":
			obj.content_san = ""
		else:
			obj.content_san = content_san

		if content_kan=="<div><br></div>":
			obj.content_kan = ""
		else:
			obj.content_kan = content_kan
		model_datastore.add(obj)

		return redirect(url_for('.list_leaves', branch_id=branch_id))

	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	branch={}
	branch_name = ""
	branch = model_datastore.read_branch(branch_id)
	branch_name = branch['name']
	try:
		branch_parent = model_datastore.read_branch(branch.branch_parent_id)
		master_branch_name = branch_parent['name']
	except:
		master_branch_name = "Root"

	#Send output
	di = {
	"branch": branch,
	"branch_name": branch_name,
	"master_branch_name": master_branch_name,
	"branch_parent_id": branch['branch_parent_id'],
	"branch_id": branch_id,
	}
	return utils.render_html("contentmgr-add.html",di)


# ========================================================
# EDIT LEAF
# ========================================================
@mod3.route('/<leaf_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(leaf_id):
	leaf = model_datastore.read_leaf(leaf_id)
	branch_id = leaf['branch_id']

	#```````````````````````````````````````````````````````````
	# POST METHOD
	#```````````````````````````````````````````````````````````
	if request.method == 'POST':
		leaf_id = leaf.id
		obj = objects.clsLeaf()
		content_eng = request.form['content_eng']
		content_san = request.form['content_san']
		content_kan = request.form['content_kan']

		if content_eng=="<div><br></div>":
			obj.content_eng = ""
		else:
			obj.content_eng = content_eng

		if content_san=="<div><br></div>":
			obj.content_san = ""
		else:
			obj.content_san = content_san

		if content_kan=="<div><br></div>":
			obj.content_kan = ""
		else:
			obj.content_kan = content_kan

		obj.update(leaf_id,branch_id,request.form['content_type_id'],request.form['source_doc_id'])
		return redirect(url_for('.list_leaves', branch_id=branch_id))

	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	#Create leaf object and populate with all data
	obj = objects.clsLeaf()
	obj.populate_from_record(leaf)

	branch_name = ""
	branch = model_datastore.read_branch(branch_id)
	branch_name = branch['name']
	try:
		branch_parent = model_datastore.read_branch(branch.branch_parent_id)
		master_branch_name = branch_parent['name']
	except:
		master_branch_name = "Root"

	#Send output
	di = {
	"leaf": obj,
	"branch": branch,
	"branch_name": branch_name,
	"master_branch_name": master_branch_name,
	"branch_id": branch_id,
	"branch_parent_id": branch['branch_parent_id']
	}
	return utils.render_html("contentmgr-edit.html",di)

# ========================================================
# DELETE LEAF
# ========================================================
@mod3.route('/<leaf_id>/delete')
@login_required
def delete(leaf_id):
	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	leaf = model_datastore.read_leaf(leaf_id)
	branch_id = leaf['branch_id']
	model_datastore.delete(leaf_id)
	return redirect(url_for('.list_leaves', branch_id=branch_id))
