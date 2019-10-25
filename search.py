#Sample code from Algolia
from _private import keys
import requests
from algoliasearch import algoliasearch
from algoliasearch.search_client import SearchClient

client = algoliasearch.Client(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for adding data to index
client = SearchClient.create(keys.ALGOLIA_APPLICATION_ID,keys.ALGOLIA_SEARCH_ONLY_API_KEY)	#Used for searching

index = client.init_index('SUTRAS')

#Adding json data to database
posts = requests.get(
    'https://alg.li/doc-media.json'
)
index.add_objects(posts.json())
