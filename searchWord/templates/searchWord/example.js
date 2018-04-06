var getPixels = require("get-pixels")
 
getPixels("rhino.jpg", function(err, pixels) {
  if(err) {
    console.log("Bad image path")
    return
  }
  console.log(pixels.shape.slice()[0,0,1])
  console.log("got pixels", pixels.shape.slice())
})


