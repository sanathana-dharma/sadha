//JS for Sanathana Dharma

$(document).ready(function() {



$('#ec-add-account-btn').click( function() {
  if ($('.frm-account').valid())
  {
    $.ajax({
        url: '/main/add_account',
        type: 'post',
        dataType: 'json',
        data: $('#ec-add-account-form').serialize()
    }).done(function (data, status, jqXHR) {
      if (!data.error_msg){
         location.replace(location.origin);
      } else {
        alert(data.error_msg);
      }
     }).fail(function (jqXHR,status,err) {
       alert("Error while adding account.");
    })
  }
});



});
