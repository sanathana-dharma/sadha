#External libraries
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import utils

#Internal imports
from treemgr import objects
from treemgr import model_datastore

#Register as Blueprint module
mod = Blueprint('treemgr', __name__, template_folder='templates')


# ===============================================================
# List child branches for a given branch
# ===============================================================
@mod.route('/list/', defaults={'branch_id': '0'}, methods=['GET', 'POST'])
@mod.route('/list/<branch_id>', methods=['GET', 'POST'])
@login_required
def list(branch_id):
	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	if branch_id != '0':
		#Displaying children of selected category
		#First fetch all children for this branch
		branches = model_datastore.list(branch_id)
		#Determine page title name
		x = model_datastore.read(branch_id)
		if x:
			catname = x['name']
		else:
			catname = "Categories"
		#Find and Fetch next branch details
		#o = objects.clsBranch()
		#branch = o.read(branch_id)
		#next_branch = o.get_next_record()
		#next_branch_id = next_branch.id

	else:
		#Displaying root categories
		catname = "Root categories"
		branches = model_datastore.list('0')
		#next_branch_id = None

	#Send output
	di = {
	"branches": branches,
	"catname": catname,
	"branch_parent_id": branch_id,
	#"next_branch_id": next_branch_id
	}
	return utils.render_html("treemgr-list.html",di)

# ===============================================================
# View details of a Branch (Not branch content, just branch details)
# ===============================================================
@mod.route('/view/<id>')
@login_required
def view(id):
	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	branch = model_datastore.read(id)

	#Send output
	di = {
	"branch": branch,
	}
	return utils.render_html("treemgr-view.html",di)

# ===============================================================
# Bulk add child branches
# ===============================================================
@mod.route('/add/', defaults={'branch_parent_id': None}, methods=['GET', 'POST'])
@mod.route('/add/<branch_parent_id>', methods=['GET', 'POST'])
@login_required
def add(branch_parent_id):
	#```````````````````````````````````````````````````````````
	# POST METHOD
	#```````````````````````````````````````````````````````````
	if request.method == 'POST':
		#Identify the parent
		branch_parent_id = request.form['branch_parent_id']
		#Fetch category names being added
		name1 = request.form['name1']
		name2 = request.form['name2']
		name3 = request.form['name3']
		name4 = request.form['name4']
		name5 = request.form['name5']
		sortorder1 = request.form['sortorder1']
		sortorder2 = request.form['sortorder2']
		sortorder3 = request.form['sortorder3']
		sortorder4 = request.form['sortorder4']
		sortorder5 = request.form['sortorder5']

		if name1:
			o1 = objects.clsBranch()
			o1.set(name1, branch_parent_id, sortorder1)
			o1.create()
		if name2:
			o2= objects.clsBranch()
			o2.set(name2, branch_parent_id, sortorder2)
			o2.create()
		if name3:
			o3 = objects.clsBranch()
			o3.set(name3, branch_parent_id, sortorder3)
			o3.create()
		if name4:
			o4 = objects.clsBranch()
			o4.set(name4, branch_parent_id, sortorder4)
			o4.create()
		if name5:
			o5 = objects.clsBranch()
			o5.set(name5, branch_parent_id, sortorder5)
			o5.create()

		return redirect(url_for('.list', branch_id=branch_parent_id))

	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	branch={}

	#Compute next sort order for the form
	o = objects.clsBranch()
	o.branch_parent_id = branch_parent_id
	next_sortorder = o.get_next_sortorder()
	#Send output
	di = {
	"branch": branch,
	"branch_parent_id": branch_parent_id,
	"next_sortorder": next_sortorder
	}
	return utils.render_html("treemgr-add.html",di)
# [END add]


# ===============================================================
# Edit details of a branch
# ===============================================================
@mod.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
	branch = model_datastore.read(id)
	branch_parent_id = branch['branch_parent_id']
	#```````````````````````````````````````````````````````````
	# POST METHOD
	#```````````````````````````````````````````````````````````
	if request.method == 'POST':
		#Identify the parent
		branch_parent_id = request.form['branch_parent_id']
		#Fetch category name being updated
		name = request.form['name']
		sortorder = request.form['sortorder']

		if name:
			o = objects.clsBranch()
			o.set(name, branch_parent_id, sortorder)
			o.id = branch.id
			o.update()

		return redirect(url_for('.list', branch_id=branch_parent_id))

	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	#Send output
	di = {
	"branch": branch,
	"branch_parent_id": branch_parent_id,
	"sortorder": branch['sortorder']
	}
	return utils.render_html("treemgr-edit.html",di)

# ===============================================================
# Delete a branch
# ===============================================================
@mod.route('/<id>/delete')
@login_required
def delete(id):
	#```````````````````````````````````````````````````````````
	# GET METHOD
	#```````````````````````````````````````````````````````````
	#Check if this branch has children, if yes we can't proceed with deletion
	#User must first delete the children inorder to delete the parent
	branch = model_datastore.read(id)
	branch_parent_id = branch['branch_parent_id']

	if utils.branch_has_children(id):
		#Dont allow delete
		print("Can't delete this branch as it has children!")
		return redirect(url_for('.list'))
	else:
		#Allow deletion
		o = objects.clsBranch()
		o.populate_from_record(branch)
		o.delete()
		print("Deleted branch successfully!")
		return redirect(url_for('.list', branch_id=branch_parent_id))
