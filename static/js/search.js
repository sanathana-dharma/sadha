
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
	instantsearch.widgets.refinementList({
    container: '#refine',
    attribute: 'branch ancestor name',
  }),
  instantsearch.widgets.hits({
    container: '#hits',
    templates: {
      item: `
					<article>
					  <h1><a href="http://sanathana-dharma-app.appspot.com/{{permalink}}">{{#helpers.highlight}}{"attribute": "branch name"}{{/helpers.highlight}}</a></h1>
						<span>{{branch ancestor name}}</span><br/>
						<span style="color:#5c9e6c;">  {{path}}</span><br/>
					</article>
`,
    },
  }),
  instantsearch.widgets.pagination({
    container: '#pagination',
  })
]);


search.start();
