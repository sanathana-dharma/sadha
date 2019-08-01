

$(document).ready(function() {

		//Load root categories on page load
		//ajax_get_call('/main/categories');
		//alert(data);

		//Handle category creation
		$('#add-category-btn').click( function() {
			ajax_post_call('/main/categories/add', '#add-category-form', '/main/categories');
		});

		//Handle category editing
		$('#edit-category-btn').click( function() {
			ajax_post_call('/main/categories/edit', '#edit-category-form','/main/categories');
		});


});
