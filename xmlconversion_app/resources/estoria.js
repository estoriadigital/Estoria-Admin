$(document).ready(function(){
	var selly = $("#pageselect-menu");
    $.each(MENU_DATA['json'], function( index, page ) {
        selly.append('<option value="' + page + '">'
             + page + '</option>');
    });
	
	$( "#pageselect-menu" ).change(function() {
		var selectedText = $(this).find("option:selected").text();
		var selectedValue = $(this).val();
		if (selectedValue === null) {
			return;
		}
		if (selectedValue === "title") {
			return;
		}
		loadJSON(function(response) {
			// Parse JSON string into object
			var actual_JSON = JSON.parse(response);
			$('.panel-body').html(processBody(actual_JSON['html_abbrev']));
			$('.hoverover').tooltipster({
               			 theme: 'tooltipster-light'
            		});
		}, selectedValue);
	});
});

function processBody(data) {
    var ret = '';
    ret += '              <span class="innerbody" data-bind="html: $data.body">' + data + '</span>\n';
    return ret;
}

// https://codepen.io/KryptoniteDove/post/load-json-file-locally-using-pure-javascript 
function loadJSON(callback, filename) {  
    var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
		xobj.open('GET', './json/' + filename + '.json', true);
		xobj.onreadystatechange = function () {
			if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
        }
    };
    xobj.send(null);  
}
