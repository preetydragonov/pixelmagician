function goTo(){
	const textValue = document.getElementById('text_box').value;
        const encoded_textValue = encodeURIComponent(textValue);
        location.replace('/loading/'+encoded_textValue, '_self');
}
goTo();
