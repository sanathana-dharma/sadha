var search_url = "/search-name";
$(document).ready(function() {
  $.fn.autocomplete = function(input_id) {
    $(input_id).select2({
      placeholder: "Search for a member",
      minimumInputLength: 3,
      allowClear: true,
      ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
          url: "/get_member_ids",
          dataType: 'json',
          quietMillis: 250,
          data: function (term, page) {
              return {
                  q: term, // search term
              };
          },
          results: function (data, page) { // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to alter the remote JSON data

              return { results: data };
          },
          cache: true
      },
      formatResult: repoFormatResult, // omitted for brevity, see the source of this page
      formatSelection: repoFormatSelection,  // omitted for brevity, see the source of this page
      dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
      escapeMarkup: function (m) { return m; } // we do not want to escape markup since we are displaying html in results
  });
  };

  $.fn.autocomplete_tags = function(input_id){
      $(input_id).select2({
      placeholder: "Search for a member",
      minimumInputLength: 3,
      maximumSelectionSize:5,
      multiple:true,
      ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
          url: "/get_member_ids",
          dataType: 'json',
          quietMillis: 250,
          data: function (term, page) {
              return {
                  q: term, // search term
              };
          },
          results: function (data, page) { // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to alter the remote JSON data

              return { results: data };
          },
          cache: true
      },
      formatResult: repoFormatResult, // omitted for brevity, see the source of this page
      formatSelection: repoFormatSelection,  // omitted for brevity, see the source of this page
      dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
      escapeMarkup: function (m) { return m; } // we do not want to escape markup since we are displaying html in results
  });
  }


    $.fn.autocomplete_tags_acc = function(input_id,url){
      $(input_id).select2({
      placeholder: "Search for a account",
      minimumInputLength: 3,
      maximumSelectionSize:5,
      multiple:true,
      ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
          url: url,
          dataType: 'json',
          quietMillis: 250,
          data: function (term, page) {
              return {
                  q: term, // search term
              };
          },
          results: function (data, page) { // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to alter the remote JSON data

              return { results: data };
          },
          cache: true
      },
      formatResult: headFormatResult, // omitted for brevity, see the source of this page
      formatSelection: headFormatResult,  // omitted for brevity, see the source of this page
      dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
      escapeMarkup: function (m) { return m; } // we do not want to escape markup since we are displaying html in results
  });
  }



  $("#searchtxt").select2({
      placeholder: "Search",
      width:200,
      minimumInputLength: 3,
      ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
          url: get_search_url,
          dataType: 'json',
          quietMillis: 250,
          data: function (term, page) {
              return {
                  q: term, // search term
              };
          },
          results: function (data, page) { // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to alter the remote JSON data

              return { results: data };
          },
          cache: true
      },
      formatResult: headFormatResult, // omitted for brevity, see the source of this page
      formatSelection: headFormatResult,  // omitted for brevity, see the source of this page
      dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
      escapeMarkup: function (m) { return m; } // we do not want to escape markup since we are displaying html in results
  });

  $("#search_type").change(function(){
    search_url = '/search-'+$(this).val();
  });
  $("#searchtxt").on('select2-selecting',function(e){
    if ($("#search_type").val() == "name" || $("#search_type").val() == "mobile")
        window.location = '/main/member_details?member_id='+e.val;
    else if ($("#search_type").val() == 'account')
        window.location = '/main/account_details?account_id='+e.val;
    else
        window.location = '/main/group_details?group_id='+e.val;
  });

});

function get_search_url(){
  return search_url;
}

function headFormatResult(member){
  if (member.phone_no)
    return member.name+'('+member.phone_no+')';
  else
    return member.name;
}

function repoFormatResult(member){
  return member.name+' ('+member.phone_no+')';
}

function repoFormatSelection(member) {
      return member.name+' ('+member.phone_no+')';
   }