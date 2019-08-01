
$(document).ready(function() {
			//Load root categories
			dynamic_categories_init();
			//Attach on change event for the selectbox
			dynamic_categories_attach_event();
})




function dynamic_categories_init(){
	var NewHTML = "";
	//Add a hidden field to hold currently selected cateogry ID

	if( $('#dyanmic_categories_lastchild_category_id').length == 0){
		NewHTML = NewHTML + "<input type='hidden' id='dyanmic_categories_lastchild_category_id' name='dyanmic_categories_lastchild_category_id' value ='' />";
		$("#dynamic_categories").append(NewHTML);
		NewHTML = "";
	}

	// Fetch initial root categories list
	$.ajax({
				url: '/main/categories/api/list?parent_category_id=',
				type: 'get',
				dataType: 'json',
				data: {},
		}).done(function (data, status, jqXHR) {
					 //Populate the fetched categories
					 //We need to simply create one new selectbox below current selectbox and sub categories in it
					 //add new selectbox to UI
						NewHTML = NewHTML + "<p>";
						NewHTML = NewHTML + "<select class= 'dynamic_category_select' category_id='' id='1' style='width:250px;'>";
						NewHTML = NewHTML + "<option value = '' selected='Selected'>Select..</option>";

						$.each(data.dict_categories, function(key, value) {
							NewHTML = NewHTML + "<option value='" + key + "'>" + value + "</option>";
					 	});

						NewHTML = NewHTML + "</select>";
						NewHTML = NewHTML + "</p>";

						$("#dynamic_categories").append(NewHTML);
			 }).fail(function (jqXHR,status,err) {
					//alert("Error loading sub categories1.");
					//alert(err);
			})

}

function dynamic_categories_attach_event(){



   	//Handle dynamic selectboxes
	  $( "#dynamic_categories" ).on( "change", ".dynamic_category_select", function() {

				var selected_category_id;
				var selectboxID = 1;
				selectboxID = this.id;
				//Identify which select box was changed - use its ID
				//We need to delete all select boxes below this using ID + 1, + 2 and so on
				//alert(selectboxID);
				var i = 0;
				i = parseInt(selectboxID) + 1;
				while (i < 10){
					$("#"+i).remove();
					i++;
				}

				//category ID of current select box is
				selected_category_id = $(this).val().toString();
				//alert(selected_category_id);
				//Set category_id for current select box based on selection
				$(this).attr("category_id",selected_category_id);
				//Also lets store the last child category ID in a hidden field for reference (Eg. adding content based on selected category)
				$("#dyanmic_categories_lastchild_category_id").val(selected_category_id);

				//Trigger event to signal category change, so other UI can be updated
				$( "#dynamic_categories" ).trigger( "event_category_refresh", selected_category_id );
				console.log( "custom event: categories refreshed - last child cateogry id=%s",selected_category_id );


				//Fetch sub categories of selected category
				$.ajax({
							// Fetch categories list
							url: '/main/categories/api/list?parent_category_id='+selected_category_id,
							type: 'get',
							dataType: 'json',
							data: {},
					}).done(function (data, status, jqXHR) {
								 //Populate the fetched categories
								 //We need to simply create one new selectbox below current selectbox and sub categories in it
								 //add new selectbox to UI
										if(Object.keys(data.dict_categories).length>0){
											var NewHTML = "";
											NewHTML = "<p><select class= 'dynamic_category_select' category_id='' id='" + (parseInt(selectboxID) + 1) + "' style='width:250px;'>";
											NewHTML = NewHTML + "<option selected='Selected'>                </option>";
											$.each(data.dict_categories, function(key, value) {
												NewHTML = NewHTML + "<option value='" + key + "'>" + value + "</option>";
										 });
											NewHTML = NewHTML + "</select></p>";
											//alert(NewHTML);
											$("#dynamic_categories").append(NewHTML);
										}
						 }).fail(function (jqXHR,status,err) {
								//alert("Error loading sub categories2.");
								//alert(err);
						})
		});



}








function ajax_post_call(url,form_name,return_url){
	$.ajax({
			url: url,
			type: 'post',
			dataType: 'json',
			data: $(form_name).serialize()
	}).done(function (data, status, jqXHR) {
		if (!data.error_msg){
			 location.replace(return_url);
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
			 return data;
		} else {
			alert("Error! %s",data.error_msg);
			return data;
		}

	 }).fail(function (jqXHR,status,err) {
		  //alert("Unable to make ajax GET call for url = %s.",url);
	 		//alert(err);
	})
}

function ajax_get_callback(url, callback_function){
	$.ajax({
			url: url,
			type: 'get',
			dataType: 'json',
			data: {},
	}).done(function (data, status, jqXHR) {
		if (!data.error_msg){
			 //location.replace(location.origin);
			 //Execute function (provided as parameter)
			 callback_function(data)
			 return 1;
		} else {
			alert("Error! %s",data.error_msg);
			return 1;
		}

	 }).fail(function (jqXHR,status,err) {
		  //alert("Unable to make ajax GET call for url = %s.",url);
	 		//alert(err);
	})
}
