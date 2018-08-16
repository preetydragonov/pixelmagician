function passWordToS3(){
	parsedQueryWord = document.currentScript.getAttribute('queryWordOnScript')
	setTimeout(function(){location.replace("/board/"+parsedQueryWord, '_self')}, 7000)
}
passWordToS3()
