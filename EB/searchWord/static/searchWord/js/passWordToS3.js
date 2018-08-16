function passWordToS3(){
	parsedQueryWord = document.currentScript.getAttribute('queryWordOnScript')
	setTimeout(function(){}, 10000)
	setTimeout(function(){location.replace("/board/"+parsedQueryWord, '_self')}, 0)
}
passWordToS3()
