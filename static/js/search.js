
const algolia_api_key = get_API_Key()
const searchClient = algoliasearch('SSR6G43F45', algolia_api_key);

const search = instantsearch({
  indexName: 'TREE',
  searchClient,
});

search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
  }),

  instantsearch.widgets.hits({
    container: '#hits',
  })
]);

search.start();
