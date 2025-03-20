$(document).ready(function() {
  $(document).on('keypress', function(e) {
    if (e.which == 13) {  // 13 is the Enter key
      $('#go').click();
    }
  });
});