from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import utils
from treemgr import objects
mod = Blueprint('treemgr', __name__, template_folder='templates')


# [START list]
@mod.route('/list/', defaults={'branch_parent_id': '0'})
@mod.route('/list/<branch_parent_id>')
@login_required
def list(branch_parent_id):
	if branch_parent_id != '0':
		#print("Listing child categories of:")
		#print(branch_parent_id)
		#Displaying children of selected category
		branches = utils.get_model().list(branch_parent_id)
		#Determine page title name
		x = utils.get_model().read(branch_parent_id)
		if x:
			catname = x['name']
		else:
			catname = "Categories"

		#Generate branch path
		#branch_path = utils.get_tree_path(branch_parent_id)
	else:
		#Displaying root categories
		#print("No branch_parent_id found, Listing root categories")
		catname = "Root categories"
		branches = utils.get_model().list('0')
		#branch_path = []

	#Send output
	di = {
	"branches": branches,
	"catname": catname,
	"branch_parent_id": branch_parent_id
	}
	return utils.render_html("list.html",di)
# [END list]

@mod.route('/viewbranch/<id>')
@login_required
def view(id):
	branch = utils.get_model().read(id)

	#Send output
	di = {
	"branch": branch,
	}
	return utils.render_html("view.html",di)

# [START add]
@mod.route('/add/', defaults={'branch_parent_id': None}, methods=['GET', 'POST'])
@mod.route('/add/<branch_parent_id>', methods=['GET', 'POST'])
@login_required
def add(branch_parent_id):
	if request.method == 'POST':
		#Identify the parent
		branch_parent_id = request.form['branch_parent_id']
		#Fetch category names being added
		name1 = request.form['name1']
		name2 = request.form['name2']
		name3 = request.form['name3']
		name4 = request.form['name4']
		name5 = request.form['name5']
		if name1:
			o1 = objects.clsBranch(None,name1, branch_parent_id)
			branch = utils.get_model().add(o1)
		if name2:
			o2 = objects.clsBranch(None,name2, branch_parent_id)
			branch = utils.get_model().add(o2)
		if name3:
			o3 = objects.clsBranch(None,name3, branch_parent_id)
			branch = utils.get_model().add(o3)
		if name4:
			o4 = objects.clsBranch(None,name4, branch_parent_id)
			branch = utils.get_model().add(o4)
		if name5:
			o5 = objects.clsBranch(None,name5, branch_parent_id)
			branch = utils.get_model().add(o5)

		return redirect(url_for('.list', branch_parent_id=branch_parent_id))
	branch={}

	#Send output
	di = {
	"branch": branch,
	"branch_parent_id": branch_parent_id,
	}
	return utils.render_html("add.html",di)
# [END add]


@mod.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
	branch = utils.get_model().read(id)

	try:
		branch_parent_id = branch['branch_parent_id']
	except:
		branch_parent_id = "not found"

	if request.method == 'POST':
		data = request.form.to_dict(flat=True)
		branch = utils.get_model().update(data, id)
		return redirect(url_for('.view', id=branch['id']))

	#Send output
	di = {
	"branch": branch,
	"branch_parent_id": branch_parent_id,
	}
	return utils.render_html("edit.html",di)


@mod.route('/<id>/delete')
@login_required
def delete(id):
	#Check if this branch has children, if yes we can't proceed with deletion
	#User must first delete the children inorder to delete the parent
	branch = utils.get_model().read(id)
	branch_parent_id = branch['branch_parent_id']

	if utils.branch_has_children(id):
		#Dont allow delete
		print("Can't delete this branch as it has children!")
		return redirect(url_for('.list'))
	else:
		#Allow deletion
		utils.get_model().delete(id)
		print("Deleted branch successfully!")
		return redirect(url_for('.list', branch_parent_id=branch_parent_id))
