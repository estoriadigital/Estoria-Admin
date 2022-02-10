 $(document).ready(function(){
	 $('.hoverover').tooltipster({
	                			 theme: 'tooltipster-light'
	             		});
	$('#toggle-abbreviations').on('click', function() {
		if (document.getElementById('abbreviated').style.display == 'block') {
			document.getElementById('abbreviated').style.display = 'none';
			document.getElementById('expanded').style.display = 'block';
		} else {
			document.getElementById('abbreviated').style.display = 'block';
			document.getElementById('expanded').style.display = 'none';
		}
	});

});
