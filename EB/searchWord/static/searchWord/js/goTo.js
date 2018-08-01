function goTo(){
	const textValue = document.getElementById("link_id").value;
        const encoded_textValue = encodeURIComponent(textValue);
        location.replace("/loading/"+encoded_textValue, '_self');
}
goTo();
