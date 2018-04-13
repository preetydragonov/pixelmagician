var AWS = require('aws-sdk');
var fs = require('fs');
AWS.config.region = 'ap-northeast-2';
var s3 = new AWS.S3();

var searchedWord = document.currentScript.getAttribute('searched-word');
var param = {
        'Bucket': 'searched-words',
        'Key': 'example1.txt',
        'Body': "123"
}

setTimeout(function(){
	if(searchWord == '1'|| searchWord == 1){
		s3.upload(param, function(err, data){
    			console.log(err);
    			console.log(data);
		});
	}else{
		location.replace("/board", '_self');
	}
}, 2000);

~


