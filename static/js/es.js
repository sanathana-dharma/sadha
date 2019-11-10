var data = {
	"query": {
    "match": {
      "name": {
        "query": "vedas",
        "type": "phrase"
      }
    }
  }
}

$(document).ready(function() {


	$.ajax({
	  method: "GET",
	  url: "https://83aca7fc0875486a87970beb0f2e6bcd.asia-northeast1.gcp.cloud.es.io:9243/tree/_search",
	  crossDomain: true,
	  async: false,
	  data: JSON.stringify(data),
	  dataType : 'json',
	  contentType: 'application/json',
	})
	.done(function( data ) {
	  console.log(data);
	})
	.fail(function( data ) {
	  console.log(data);
	});

});
