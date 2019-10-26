from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import utils
from contentmgr import objects
from contentmgr import model_datastore

#Register as Blueprint module
mod3 = Blueprint('contentmgr', __name__, template_folder='templates')


# [START list]
'''
@mod3.route('/list/<branch_id>')
@login_required
def list(branch_id):
	try:
		#Displaying leaves under this branch
		recs = model_datastore.list(branch_id)
		#Send output
		di = {
		"leaves": recs,
		"catname": "Branch Name will appear here",
		"branch_id": branch_id
		}
		return utils.render_html("list.html",di)

	except:
		return "Sorry! Invalid branch_id provided, cant continue."
'''
# [END list]

@mod3.route('/view/<branch_id>')
@login_required
def list_leaves(branch_id):
		print("Inside content mgr view...")
		recs = model_datastore.list_leaves(branch_id)
		branch = model_datastore.read_branch(branch_id)

		di = {}

		lsteng = []
		lstsan = []
		lstkan = []

		for x in recs:
			di = {
			"leaf_id": x.id,
			"content_eng": x['content_eng']
			}
			lsteng.append(di.copy())
			di.clear()

			di = {
			"leaf_id": x.id,
			"content_san": x['content_san']
			}
			lstsan.append(di.copy())
			di.clear()

			di = {
			"leaf_id": x.id,
			"content_kan": x['content_kan']
			}
			lstkan.append(di.copy())
			di.clear()

		#Send output
		di = {
		"lsteng": lsteng,
		"lstsan": lstsan,
		"lstkan": lstkan,
		"catname": branch['name'],
		"branch_id": branch_id
		}
		return utils.render_html("contentmgr-list.html",di)

# [START add]
@mod3.route('/add/<branch_id>', methods=['GET', 'POST'])
@login_required
def add(branch_id):
	if request.method == 'POST':
		#Fetch content being added
		content_eng = request.form['content_eng']
		content_san = request.form['content_san']
		content_kan = request.form['content_kan']
		obj = objects.clsLeaf(None,branch_id)
		if content_eng:
			obj.content_eng = content_eng
		if content_san:
			obj.content_san = content_san
		if content_kan:
			obj.content_kan = content_kan
		model_datastore.add(obj)

		return redirect(url_for('.list_leaves', branch_id=branch_id))
	branch={}

	#Send output
	di = {
	"branch": branch,
	"branch_id": branch_id,
	}
	return utils.render_html("contentmgr-add.html",di)
# [END add]


@mod3.route('/<leaf_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(leaf_id):
	leaf = model_datastore.read_leaf(leaf_id)
	branch_id = leaf['branch_id']

	if request.method == 'POST':
		data = request.form.to_dict(flat=True)
		leaf = model_datastore.update(data, leaf_id)
		return redirect(url_for('.list_leaves', branch_id=branch_id))

	branch={}
	#Send output
	di = {
	"leaf": leaf,
	"branch": branch,
	"branch_id": branch_id,
	}
	return utils.render_html("contentmgr-edit.html",di)


@mod3.route('/<leaf_id>/delete')
@login_required
def delete(leaf_id):
	leaf = model_datastore.read_leaf(leaf_id)
	branch_id = leaf['branch_id']
	model_datastore.delete(leaf_id)
	return redirect(url_for('.view', branch_id=branch_id))
