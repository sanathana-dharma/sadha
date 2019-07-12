
function ajax_post_call(url,form_name){
	$.ajax({
			url: url,
			type: 'post',
			dataType: 'json',
			data: $(form_name).serialize()
	}).done(function (data, status, jqXHR) {
		if (!data.error_msg){
			 //location.replace(location.origin);
		} else {
			alert(data.error_msg);
		}
	 }).fail(function (jqXHR,status,err) {
		  alert("Unable to make ajax call for form: %s", form_name);
	 		alert(err);
	})
}


function ajax_get_call(url){
	$.ajax({
			url: url,
			type: 'get',
			dataType: 'json',
			data: {},
	}).done(function (data, status, jqXHR) {
		if (!data.error_msg){
			 //location.replace(location.origin);
			 return 1;
		} else {
			alert(data.error_msg);
			return 1;
		}

	 }).fail(function (jqXHR,status,err) {
		  //alert("Unable to make ajax GET call for url = %s.",url);
	 		//alert(err);
	})
}


$(document).ready(function() {

		//Load root categories on page load
		data = ajax_get_call('/main/categories/api/list');
		alert(data);
/*
		if (data != null){
			//Call was success, so lets use the data fetched
			alert(data.dict_categories.length);
		}else{
			alert("false");
		}
*/
		//Handle category creation
		$('#add-category-btn').click( function() {
			ajax_post_call('/main/categories/add', '#add-category-form');
		});

		//Handle category editing
		$('#edit-category-btn').click( function() {
			ajax_post_call('/main/categories/edit', '#edit-category-form');
		});

		//Handle dynamic selectboxes
		$( "#dynamic_categories" ).on( "change", ".dynamic_category_select", function() {

					var selectboxID = 1;
					selectboxID = this.id;
					//Identify which select box was changed - use its ID
					//We need to delete all select boxes below this using ID + 1, + 2 and so on
					var i = 0;
					i = parseInt(selectboxID) + 1;
					while (i < 10){
						$("#"+i).remove();
						i++;
					}
					//category ID of current select box is
					var selected_category_id;
					selected_category_id = $(this).val().toString();
					//Set category_id for current select box based on selection
					$(this).attr("category_id",selected_category_id);
					//Fetch sub categories of selected category
					$.ajax({
								// Fetch categories list
								url: '/main/categories/list?parent_category_id='+selected_category_id,
								type: 'get',
								dataType: 'json',
								data: {},
						}).done(function (data, status, jqXHR) {
									 //Populate the fetched categories
									 //We need to simply create one new selectbox below current selectbox and sub categories in it
									 //add new selectbox to UI
									if(Object.keys(data.dict_categories).length>1){
										var NewHTML = "";
					 					NewHTML = "<p><select class= 'dynamic_category_select' category_id='' id='" + (parseInt(selectboxID) + 1) + "' style='width:250px;'>";
										NewHTML = NewHTML + "<option selected='Selected'>                </option>";
									  $.each(data.dict_categories, function(key, value) {
											NewHTML = NewHTML + "<option value='" + key + "'>" + value + "</option>";
									 });
					 					NewHTML = NewHTML + "</select></p>";
										$("#dynamic_categories").append(NewHTML);
									}
							 }).fail(function (jqXHR,status,err) {
									alert("Error loading sub categories.");
									alert(err);
							})
		});



	function addSelectOptions(select_options) {
	  var select = $('.parent-category-select');
	  $.each(select_options, function(key, value) {
	    var option = $('<option></option>');
	    option.attr('value', key);
	    option.text(value);
	    select.append(option);
	 });
};





  if( $.isFunction($.fn.validate) ) {
        jQuery.validator.addMethod("nameformat", function(value, element) {
            return this.optional(element) || /^[a-z0-9.\s]+$/i.test(value);
    }, "Please enter letters only");
    var validobj = $('.frm-account').validate({
        rules: {
                name:{
                    required:true,
                    nameformat:true
                },
                account_admin:{
                  required:true
                },
                account_admin_mail_id:{
                  email:true
                },
                balance:{
                    digits:true
                },
              },
        ignore: ".ignore, .select2-input"
    });
  }




});
