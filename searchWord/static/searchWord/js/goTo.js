function goTo(){
	const textValue = document.getElementById("link_id").value;
        const encoded_textValue = encodeURIComponent(textValue);
        //window.open("{% url 'home' %}", '_self');
        location.replace("/loading/"+encoded_textValue, '_self');
        //window.open("http://www.google.com/search?q="+textValue+"&source=lnms&tbm=isch",'_self');
}
