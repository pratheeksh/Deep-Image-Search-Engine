// ----- custom js ----- //

// sanity check
console.log( "ready!" );
$("#searching").hide();
$("#results-table").hide();
$("#error").hide();


$(function() {

  // sanity check
  console.log( "ready123!" );
  // remove active class
  $(".img").removeClass("active")
  
  // image click
  $(".img").click(function() {

    // empty/hide results
    $("#results").empty();
    $("#results-table").hide();
    $("#error").hide();

    // add active class to clicked picture
    $(this).addClass("active")

    // grab image url
    var image = $(this).attr("src")
    console.log(image)

    // show searching text
    $("#searching").show();
    console.log("searching...")


    // ajax request
    $.ajax({
      type: "GET",
      url: "/search",
      data : { img : image,
                  txt : 'sunset' },
      // handle success
      success: function(jsonResponse) {
        console.log("Success something received")
        var obj = JSON.parse(jsonResponse);
        var data = obj.results
        console.log(data)
        // show table
        $("#results-table").show();
        // loop through results, append to dom
        for (i = 0; i < data.length; i++) {
        $("#results").append('<tr><th><a href="'+data[i]["flickr"]+'"><img src="'+data[i]["image_url"]+
    '" class="result-img"></a></th><th>'+data[i]['title']+'</th><th>'+data[i]['text']+'</th><th>'+data[i]['source']+'</th></tr>')
       };



      },
      // handle error
      error: function(error) {

        console.log(error);
      }
    });

  });

  // button click
  $("#btn").click(function() {
    var start = new Date().getTime();

    // empty/hide results
    $("#results").empty();
    $("#results-table").hide();
    $("#results-heading").hide();
    $("#error").empty();
    $("#delay").empty();


    // $("#uploadedimage").empty()

    // add active class to clicked picture
    // $(this).addClass("active")

    // grab image url
    var image = $('#imagename').val()
    if (!image || 0 === image.length) {
      console.log("Changing image")
      image = 'http://'
    }
    console.log(image)
    var text = $('#textsearch').val()
    console.log(text)

    // show searching text
    $("#searching").show();
    console.log("searching...")


    // ajax request
    $.ajax({
      type: "GET",
      url: "/search",
      data : { img : image,
                  txt : text },
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