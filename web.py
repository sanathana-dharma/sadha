import webapp2
from views import base_handler
from views import index_handler
from views import category_handler
from views import api_handler

DEBUG=False

application = webapp2.WSGIApplication([ 	('/', index_handler.RedirectMainHandler),
											('/main/index', index_handler.IndexHandler),
											('/main/categories', category_handler.CategoryListHandler),
											('/main/categories/api/list', category_handler.API_CategoryList),
									 		('/main/categories/add', category_handler.AddCategoryHandler),
									 		('/main/categories/edit', category_handler.EditCategoryHandler),
	                                     ],
                                      debug=True)


def main():
  application.run()


if __name__ == "__main__":
  main()
