// download descriptor table 
$(document).ready(function(){
    $('button#descriptor_download').on('click', function(e) {
        var name = $(this).attr("name");
        // create a url location with selected descriptor
        window.location.assign(`/apdb/home/browse-descriptors/download?descriptor=${name}`);

         // display info message
         $('.info-message').find('p').text('Please wait...');
         // set timeout
         setTimeout(function(){
             $('.info-message').find('p').text('');
         }, 2000);
         // prevent reloading
         e.preventDefault() 
    });
});



// download embedding model
$(document).ready(function(){
    $('button#model_download').on('click', function(e) {
        var name = $(this).attr("name");
        // create a url location with selected model
        window.location.assign(`/apdb/home/browse-similarities/download?model=${name}`);

        // display info message
        $('.info-message').find('p').text('Model downloaded!');
        // set timeout
        setTimeout(function(){
            $('.info-message').find('p').text('');
        }, 2000);
        // prevent reloading
        e.preventDefault()
    });
});



// download database
$(document).ready(function(){
    $('button#db_download').on('click', function(e) {
        var name = $(this).attr("name");
        // create a url location with selected format
        window.location.assign(`/apdb/downloads-contacts/db?format=${name}`);

        // display info message
        $('.info-message').find('p').text('Database downloaded!');
        // set timeout
        setTimeout(function(){
            $('.info-message').find('p').text('');
        }, 2000);
        // prevent reloading
        e.preventDefault()
    });
});



// download filtered columns
$(document).ready(function() {
    //get actual header and column index
    var headerArray = [];
    var idx = [];
    var filteredArray = []
    // iterate over table columns
    var header = $("table thead tr").find('th');
    header.each(function() { idx.push($(this).index()); })
    header.each(function() { headerArray.push($(this).text()); })
    filteredArray = $.merge([headerArray], [idx]);
    // set value
    $("#header").val(JSON.stringify(filteredArray)).trigger('change');

    $("input:checkbox").click(function(){
        //get actual header and column index
        var headerArray = [];
        var idx = [];
        var filteredArray = []
        // iterate over table columns
        var header = $("table thead tr").find('th:visible');
        header.each(function() { idx.push($(this).index()); })
        header.each(function() { headerArray.push($(this).text()); })
        filteredArray = $.merge([headerArray], [idx]);
        // set value
        $("#header").val(JSON.stringify(filteredArray)).trigger('change'); 
        
    });
});
