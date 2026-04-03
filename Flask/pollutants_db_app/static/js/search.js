
// search molecules based on selected id
$(document).ready(function(){ 
  // on change selected option 
  $('#mol_id_option').on('change', function() {
    // get list of id options
    var TextSearch = $('#mol_id_list').val().replace(/'/g, '"');
    // get selected id option
    var SelectedOption = $(this).val(); 
    // create array of values
    const ArraySearch = JSON.parse(TextSearch).map(String);
    var found =  ArraySearch.includes(SelectedOption);
    // check if id option is in array 
    if (found == true) {
      // create a url location with selected id option
      window.location.assign(`/apdb/home/browse-molecules?id_option=${SelectedOption}`);
    } else {
      // clear input text 
      $('#mol_id_option').val("");
    }
  });
});


// search bioassays based on selected id
$(document).ready(function(){ 
  // on change selected option 
  $('#bio_id_option').on('change', function() {
    // get list of id options
    var TextSearch = $('#bio_id_list').val().replace(/'/g, '"');
    // get selected id option
    var SelectedOption = $(this).val(); 
    // create array of values
    const ArraySearch = JSON.parse(TextSearch).map(String);
    var found =  ArraySearch.includes(SelectedOption);
    // check if id option is in array
    if (found == true) {
      // create a url location with selected id option
      window.location.assign(`/apdb/home/browse-bioassays?id_option=${SelectedOption}`);
    } else {
      // clear input text 
      $('#bio_id_option').val("");
    }
  });
});


// search similar molecules based on input id
$(document).ready(function(){ 
  // on enter key press
  $(document).on('keypress',function(e) {
    if(e.which == 13) {  
      if ($.trim($('textarea#molecule_id').val()) != "") {
        // get list of id values 
        var TextSearch = $('input#molecule_ids').val().replace(/'/g, '"');
        // get input id 
        var SearchTerm = $.trim($("textarea#molecule_id").val());
        // create array of values 
        const ArraySearch = JSON.parse(TextSearch).map(String);
        var found =  ArraySearch.includes(SearchTerm);
        // check if id is in array 
        if (found == true) {
          var threshold = 0.95;
          // create a url location with input id and threshold
          window.location.assign(`/apdb/home/browse-similarities/panel?molecule_id=${SearchTerm}&similarity_thr=${threshold}`);
        } else {
          // display alert message 
          e.preventDefault();
          $('.info-alert').find('p').text('Invalid ID. Try again!');
          setTimeout(function(){
            $('.info-alert').find('p').text("");
        }, 2000);
          // clear input textarea 
          $('textarea#molecule_id').val("");
        } 
      } 
    }
  });
});

