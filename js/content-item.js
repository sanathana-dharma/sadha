
$(document).ready(function() {

		//Load root categories on page load
		data = ajax_get_call('/main/content');
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
