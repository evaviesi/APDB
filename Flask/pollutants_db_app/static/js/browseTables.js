
// molecules table
$(document).ready(function() {
  $('#molecule_table').dynatable({
    features: {
      search: false,
      }, 
    table: {
      copyHeaderClass: true
    }
  });
});


// bioassays table
$(document).ready(function() {
  $('#bioassay_table').dynatable({
    features: {
      search: false,
    },
    table: {
      copyHeaderClass: true
    }
  });
});


// periodic table 
$(document).ready(function() {
  $('li[class^="type-"]').mouseover(function(){
    var currentClass = $(this).attr('class').split(' ')[0];
    if(currentClass != 'empty'){
      $('.main > li').addClass('deactivate');
      $('.' + currentClass).removeClass('deactivate');
    }
  });
 
 $('li[class^="cat-"]').mouseover(function(){
    var currentClass = $(this).attr('class').split(' ')[0];
      $('.main > li').addClass('deactivate');
      $('.' + currentClass).removeClass('deactivate');
  }); 
  
  $('.main > li').mouseout(function(){
    var currentClass = $(this).attr('class').split(' ')[0];
     $('.main > li').removeClass('deactivate');
     $('.' + currentClass).removeClass('deactivate');
  }); 

  // filter matrix based on periodic table element
  $('.main > li').click(function(){
    //var atom = $(this).html().split("<")[0]
    var atom = $(this).html();

    if(atom.length == 1) {
      // create a url location with filtered element 
      window.location.assign(`/apdb/home/browse-molecules/filter?element=${atom.toUpperCase()}`);
    } else {
      window.location.assign(`/apdb/home/browse-molecules/filter?element=${atom}`);
    }
 });
});


// get similar molecules from molecules table 
$(function(){
  $('#molecule_table tbody').on('click', 'td > a', function() {
    var selected_cid = $(this).text();
    var threshold = 0.95;
    // create a url location with filtered id
    window.location.assign(`/apdb/home/browse-similarities/panel?molecule_id=${selected_cid}&similarity_thr=${threshold}`);
  });
});


// get similar molecules from similarities table
$(function(){
  $('#molecule_similarity_table td > div > a').click(function(){
    var selected_cid = $(this).text();
    var threshold = 0.95;
    // create a url location with filtered id
    window.location.assign(`/apdb/home/browse-similarities/panel?molecule_id=${selected_cid}&similarity_thr=${threshold}`);
  });
});


// get selected similarity threshold 
$(function(){ 
  $('#similarity_btn').click(function(){
    const urlParams = new URLSearchParams(window.location.search);
    // get selected parameters
    var current_cid = urlParams.get('molecule_id');
    var selected_threshold = $('#similarity_thr').val();
    // check if higher than max
    if (selected_threshold > $('#similarity_thr').attr('max')) {
      selected_threshold = 0.95
    // check if lower than min
    } else if (selected_threshold < $('#similarity_thr').attr('min')) {
      selected_threshold = 0.75
    }
    // create a url location with filtered cid and selected threshold
    window.location.assign(`/apdb/home/browse-similarities/panel?molecule_id=${current_cid}&similarity_thr=${selected_threshold}`);
  });    
  // set current similarity threshold 
  const urlParams = new URLSearchParams(window.location.search);
  var current_threshold = urlParams.get('similarity_thr');
  $('#similarity_thr').attr('value', current_threshold)
});


// get selected targets from bioassays table 
$(function(){
  $('#bioassay_table tbody').on('click', 'td > a', function() {
    var selected_uniprotkb = $(this).text();
    // create a url location with filtered id
    window.location.assign(`/apdb/home/browse-targets?target_uniprotkb=${selected_uniprotkb}`);
  });
});


// get similar molecules from targets panel
$(function(){
  $('#molecules_target_table td > a').click(function(){
    var selected_cid = $(this).text();
    var threshold = 0.95;
    // create a url location with filtered id
    window.location.assign(`/apdb/home/browse-similarities/panel?molecule_id=${selected_cid}&similarity_thr=${threshold}`);
  });
});
