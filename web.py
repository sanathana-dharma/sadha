import webapp2
from views import base_handler
from views import index_handler
from views import category_handler
from views import content_handler
from views import search_handler
from views import api_handler

DEBUG=False

application = webapp2.WSGIApplication([ 	('/', index_handler.RedirectMainHandler),
											('/main/index', index_handler.IndexHandler),
											('/main/categories', category_handler.CategoryListHandler),
											('/main/categories/api/list', category_handler.API_CategoryList),
									 		('/main/categories/add', category_handler.AddCategoryHandler),
									 		('/main/categories/edit', category_handler.EditCategoryHandler),
											('/main/content', content_handler.ContentListHandler),
											('/main/content/api/list', content_handler.API_ContentList),
									 		('/main/content/add', content_handler.AddContentHandler),
									 		('/main/content/edit', content_handler.EditContentHandler),
										    ('/main/search', search_handler.MainSearchPage),
										    ('/main/sign', search_handler.SearchComment),
	                                     ],
                                      debug=True)


def main():
  application.run()


if __name__ == "__main__":
  main()
