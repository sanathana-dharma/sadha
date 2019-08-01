
$(document).ready(function() {

		//Load root categories on page load
		//data = ajax_get_call('/main/content');
		//alert(data);

		//Handle category creation
		$('#add-content-btn').click( function() {
			ajax_post_call('/main/content/add', '#add-content-form', '/main/content');
		});

		//Handle category editing
		$('#edit-content-btn').click( function() {
			ajax_post_call('/main/content/edit', '#edit-content-form','/main/content');
		});


});

//This event occurs when category is changed
//So here we can trigger any change in UI related to this event
$( "#dynamic_categories" ).on( "event_category_refresh", function( event, selected_category_id ) {
			//Make an ajax call with call back function
		//	alert("custom event start");
			ajax_get_callback('/main/content/api/list?category_id='+selected_category_id, event_category_refresh_func);
		//	alert("custom event complete");


});

//This function is executed after the ajax call is successful
function event_category_refresh_func(data){
//alert(data);
	var NewHTML = "";
	NewHTML = NewHTML + "<!-- TABLE --><table class='table table-striped table-condensed'><thead><tr><th>Content</th><th>&nbsp;</th></tr></thead><tbody>";

	if(Object.keys(data.dict_content_items).length>0){
			$.each(data.dict_content_items, function(key, value) {

				NewHTML = NewHTML + "<tr><td><a href='/main/content/edit?content_item_id="+key+"'>" + value + "</a></td>";
				NewHTML = NewHTML + "<td><a href='/main/content/edit?content_item_id="+key+"'><button class='btn button-symbol'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button></a>&nbsp;</td></tr>";
			});
		}
		else {
			NewHTML = NewHTML + "<span>No content items</span>";
		}
		NewHTML = NewHTML + "</tbody></table><!-- // TABLE -->";
	$("#dynamic_content_table").html(NewHTML);
}
