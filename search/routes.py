from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import utils
from treemgr import objects as treemgr_objects
from search import objects as search_objects
from treemgr import model_datastore

#Search related imports
from _private import keys
import requests
from algoliasearch.search_client import SearchClient

#Elastic
from elasticsearch import Elasticsearch
from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Q
import certifi
from elasticsearch_dsl import connections, Search, Q
from elasticsearch_dsl.query import Match, MultiMatch

#Register as Blueprint module
mod4 = Blueprint('search', __name__, template_folder='templates')


@mod4.route("/testpush")
def test_push():
	#client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for adding data to index
	client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_ADMIN_API_KEY)	#Used for searching
	index = client.init_index('TREE')

	branch = [
			{"branch_parent_id": "767","name": "Test6"},
			{"branch_parent_id": "878","name": "Test7"},
	]
	index.save_objects(branch, {'autoGenerateObjectIDIfNotExist': True})
	print("Test data pushed to Index")
	return "Test data pushed to Index"

	#Adding json data to database
	#posts = requests.get(
	#    'https://alg.li/doc-media.json'
	#)
	#index.add_objects(posts.json())


@mod4.route("/es2")
def es2():

	return "Added!"

@mod4.route("/esquery")
def es_query():
	es = search_objects.clsElasticIndex()
	q = Q('match', title='world2')
	return es.execute_query('blog',q)
	#गच्छति
