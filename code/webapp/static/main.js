// ----- custom js ----- //

// sanity check
 console.log( "ready!" );

$(function() {

  // sanity check
  console.log( "ready!" );

  // image click
  $(".img").click(function() {

    // add active class to clicked picture
    $(this).addClass("active")

    // grab image url
    var image = $(this).attr("src")
    console.log(image)

    // ajax request
    $.ajax({
      type: "POST",
      url: "/search",
      data : { img : image },
      // handle success
      success: function(result) {
        console.log(result.results);
      },
      // handle error
      error: function(error) {
        console.log(error);
      }
    });

  });

});