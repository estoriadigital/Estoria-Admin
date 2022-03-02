var source = $("#some-template").html();
var template = Handlebars.compile(source);

callback = function(data) {
    var output_data = {apparati: []};
    var apparati = data['structure']['apparatus']
    var arrayLength = apparati.length;
    for (var i = 0; i < arrayLength; i++) {
        output_readings = [];
        readings = apparati[i]['readings'];
        var readings_length = readings.length;
        var overtext_witnesses_list = [];
        for (var j = 0; j < readings_length; j++) {

            var reading = readings[j];
            var witnesses = reading['witnesses']
            if (j == 0) {
                overtext_witnesses_list = witnesses;
            }
            var tokens = reading['text']
            var tokens_length = tokens.length;
            var reading_tokens = [];
            for (var k = 0; k < tokens_length; k++) {
                var token = tokens[k];
                reading_tokens.push(token['interface']);
            }
            var text = reading_tokens.join(' ');

            if (witnesses.length == 1) {
                if (witnesses[0] == 'E2') {
                    if (text == '') {
                        if ($.inArray('E1', overtext_witnesses_list)) {
                            // We got nonsense
                            //output_readings[output_readings.length - 1].has_variants = false;
                            continue;
                        }
                    }
                } else if (witnesses[0] == 'E1') {
                    if (text == '') {
                        if ($.inArray('E2', overtext_witnesses_list)) {
                            // We got nonsense
                            //output_readings[output_readings.length - 1].has_variants = false;
                            continue;
                        }
                    }
                }
            }
            console.log(witnesses)



            var text_witnesses = witnesses.join(' ');
            output_readings.push(
                {witnesses: text_witnesses,
                 text: text,
                }
            );
        }
        output_data['apparati'].push({
            start: apparati[i]['start'],
            end: apparati[i]['end'],
            readings: output_readings
        })
        //Do something
    }
    console.log(output_data);
    $('body').append(template(output_data));

}


// var context = COLLATION.read_params()['context']
var context = document.getElementById('context').value;
var filename = document.getElementById('collations_path').value + '/' + context + ".json"
console.log(filename);
COLLATION.read_JSON_file(filename, callback)
