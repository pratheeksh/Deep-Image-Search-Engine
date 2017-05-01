// ----- custom js ----- //

// sanity check
console.log( "ready!" );
$("#searching").hide();
$("#results-table").hide();
$("#error").hide();


$(function() {

    // Variable to store your files
	var files;
	var filename="Empty";
   // Add events
	$('input[type=file]').on('change', prepareUpload);
	$('form').on('submit', uploadFiles);

	// Grab the files and set them to our variable
	function prepareUpload(event)
	{

		files = event.target.files;
		console.log(files)
	}

	// Catch the form submit and upload the files
	function uploadFiles(event)
	{
		event.stopPropagation(); // Stop stuff happening
        event.preventDefault(); // Totally stop stuff happening

        // START A LOADING SPINNER HERE

        // Create a formdata object and add the files
		var data = new FormData();
		$.each(files, function(key, value)
		{
			data.append(key, value);
		});

        $.ajax({
            url: 'upload?files',
            type: 'POST',
            data: data,
            cache: false,
            dataType: 'text',
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(jsonResponse)
            {
            filename = jsonResponse
            console.log("Success Image stored as ", jsonResponse)

            },
            error: function(response)
            {
            	console.log('ERRORS: ' + response);
            }
        });
    }

  // button click
  $("#btn").click(function() {
    var start = new Date().getTime();
    // empty/hide results
    $("#results").empty();
    $("#results-table").hide();
    $("#results-heading").hide();
    $("#error").empty();
    $("#delay").empty();


    console.log(image)
    var text = $('#textsearch').val()
    console.log(text)

    // show searching text
    $("#searching").show();
    console.log("searching...")


    // grab image url
    var image = $('#imagename').val()
    if (!image || 0 === image.length) {
      console.log("Changing image")
      image = 'http://'
    }

    // check if anything was uploaded
    if (filename) {
      
      console.log("Uploaded file was saved here ", filename)
    }


    // ajax request
    $.ajax({
      type: "GET",
      url: "/search",
      data : { img : image,
                  txt : text, load : filename},
      // handle success
      success: function(jsonResponse) {
        console.log("Success something received")
        var obj = JSON.parse(jsonResponse);
        var data = obj.results
        console.log(data)
        // show table
        $("#results-heading").show();
        $("#results-table").show();


        // loop through results, append to dom
        // $("#results").append('<h2 id="results-heading">Results</h2>')
        for (i = 0; i < data.length; i++) {
        $("#results").append('<tr><td class="col-md-3"><a href="'+data[i]["flickr"]+'"><img src="/static/images/'+data[i]["doc_id"]+".jpg"+
    '" width=200 height=200></a></td><td class="col-md-2">'+data[i]['title']+'</td><td class="col-md-4">'+data[i]['text']+'</td><td class="col-md-2">'+data[i]['tags']+'</td><td class="col-md-1">'+data[i]['source']+'</td></tr>')
       };
        var delay = "Total results: " + data.length + " Delay: " + (new Date().getTime() - start) / 1000.0 + " seconds";
        console.log(delay)
        $("#delay").text(delay);
        $("#delay").show()

      },
      // handle error
      error: function(error) {

        var errorText = error.statusText;
        $("#error").text(errorText  + ". Try a different image or try again after some time!");
         $("#error").show();
        console.log(error);
      }
    });

  });

});