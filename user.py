from flask_login import UserMixin
from utils import from_datastore
from google.cloud import datastore
from utils import get_client


class User(UserMixin):
	def __init__(self, id_, name, email, profile_pic):
		self.userid = id_
		self.name = name
		self.email = email
		self.profile_pic = profile_pic

	@staticmethod
	def get(user_id):
		ds = get_client()
		key = ds.key('User')
		query = ds.query(kind='User')
		query.add_filter('userid', '=', user_id)
		results = list(query.fetch(limit=1))
		for x in results:
			if not x:
				return None
			#print("user rec=")
			#print(x)
			user = User(
			    id_=x['userid'], name=x['name'], email=x['email'], profile_pic=x['profile_pic']
			)
			#print("user obj name=")
			#print(user.name)
			return user

	def get_id(self):
		return (self.userid)

	@staticmethod
	def create(id_, name, email, profile_pic):
		ds = get_client()
		key = ds.key('User')
		entity = datastore.Entity(key= key)
		entity.update({
			"userid": id_,
			"name": name,
			"email": email,
			"profile_pic": profile_pic
		})
		ds.put(entity)
