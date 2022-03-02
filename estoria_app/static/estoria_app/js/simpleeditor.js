var save_text = function () {
    var bake, params;
    params = get_params(location.search);
    if (params.hasOwnProperty('bake')) {
	bake = params['bake'];
    }
    if (typeof(bake) == "undefined") {
        console.log("Not baking, just viewing");
        return;
    }
    if (bake === "yes") {
        console.log("Baking file.");
        var allofit = $('div.container').html();
        var chapter = document.getElementById('chapter').value;
        var output = {
            chapter: chapter,
            html: allofit,
            code: bake
        };
        var url = "/api/bake/" + chapter;
        $.ajax(url, {
            data : JSON.stringify(output),
            contentType : 'application/json',
            type : 'POST',
        });
    } // End if bake
};

var get_params = function (search_string) {
    var params, pairs, temp, i;
    params = {};
    pairs = search_string.replace('?', '').split('&');
    for (i = 0; i < pairs.length; i += 1) {
	   temp = pairs[i].split('=');
	   params[temp[0]] = temp[1];
    }
    return params;
};

var get_base_witness = function(page) {
    var page_number;
    page_number = parseInt(page);
    if (page_number < 575) {
        return 'E1';
    } else if (page_number < 626) {
        return 'E2';
    } else if (page_number < 656) {
        return 'E2';
    } else if (page_number < 821) {
        return 'T';
    }
};

// * E1 from 1 to 574
// * E2 from 575 to 626
// * Y from 627 to 656
// * T from 657 to 820
// Between 627 and 820, occasionally Y or T has text missing. In these cases the base text reverts to E2.

var test_base_missing = function(page) {
    if (page > 626) {
        return true;
    }
};


var process_data = function (data, overtext_template, variant_template) {

    var variants, output_readings, real_variants, context,
    verse_number_from_json, apparatus, arrayLength, i, readings,
    overtext_witnesses, j, k, reading, witnesses, tokens, reading_tokens,
    token, text, chapter_and_verse, verse_id_name, chapter_id_name, is_rubric,
    overtext_witnesses_list, params;

    variants = [];
    output_readings = [];
    real_variants = [];
    context = data.context;
    verse_number_from_json = context.split("S")[1];
    apparatus = data.structure.apparatus;
    for (i = 0; i < apparatus.length; i+=1) {
        readings = apparatus[i].readings;
        overtext_witnesses = "";
        for (j = 0; j < readings.length; j+=1) {
            reading = readings[j];
            witnesses = reading.witnesses;
            tokens = reading.text;
            reading_tokens = [];
            for (k = 0; k < tokens.length; k+=1) {
                token = tokens[k];
                reading_tokens.push(token['interface']);
            }
            text = reading_tokens.join(' ');
            chapter_and_verse = context.split("S");
            verse_id_name = chapter_and_verse[1];
            chapter_id_name = chapter_and_verse[0].split('D')[1];
            is_rubric = 0;
            if (verse_id_name == "Rubric") {
                is_rubric = 1;
            }
            /** this is where we fix the rubrics **/
            if (j === 0) {
                overtext_witnesses = witnesses.join(' ');
                overtext_witnesses_list = witnesses;
                output_readings.push(
                    {text: text,
                     id: context + '_' + i,
                     i: i,
                     has_variants: true,
                     is_rubric: is_rubric,
                     chapter_name: chapter_id_name
                    }
                );
            } else {
                if (witnesses.length == 1) {
                    if (witnesses[0] == 'E2') {
                        if (text === '') {
                            if ($.inArray('E1', overtext_witnesses_list)) {
                                // We got nonsense
                                //output_readings[output_readings.length - 1].has_variants = false;
                                continue;
                            }
                        }
                    } else if (witnesses[0] == 'E1') {
                        if (text === '') {
                            if ($.inArray('E2', overtext_witnesses_list)) {
                                // We got nonsense
                                //output_readings[output_readings.length - 1].has_variants = false;
                                continue;
                            }
                        }
                    }
                }

                //real_variants.push(i);
                // here
                var witnesses_length = witnesses.length;
                var formatted = [];
                var formatted_wit;
                var context_key;
                var witness_name;
                var short_wit_name;
                var new_m;
                var ms_page;
                context_key = context;
                if (context.endsWith("Rubric")) {
                    context_key = 'D' + chapter_id_name + 'S100';
                }
                for (var m = 0; m < witnesses_length; m++) {

                    witness_name = witnesses[m];
                    if (witness_name.includes('-mod')) {
                        short_wit_name = witness_name.split('-mod')[0];
                        ms_page = PAGE_CHAPTER_INDEX[short_wit_name][context_key];
                    } else {
                        ms_page = PAGE_CHAPTER_INDEX[witnesses[m]][context_key];
                    }
                    if (ms_page) {
                        formatted_wit = '<span class="witname" data-page-name="' + ms_page + '">' + witnesses[m] + '</span>';
                        formatted.push(formatted_wit);
                    } else {
                        //console.log("If get here, the data is broken.", m, context_key, witnesses[m]);
                        formatted_wit = ms_page;
                    }
                }
                var text_formatted_witnesses = formatted.join(' ');
                if (text_formatted_witnesses != "") {
                    real_variants.push(i);
                    /* this may need to be fixed for multiple over text witnesses */
                    var last_over_wit = overtext_witnesses.split(' ')[1];
                    if (overtext_witnesses == "Base") {
                        last_over_wit = get_base_witness(chapter_id_name);
                        //console.log("Hello1", chapter_id_name, overtext_witnesses, last_over_wit);
                    } else {
                        //console.log("Hello2", overtext_witnesses, last_over_wit);
                    }
                    var overtext_page_name = PAGE_CHAPTER_INDEX[last_over_wit][context_key];
                    var text_witnesses = witnesses.join(' ');
                    variants.push(
                        {witnesses: text_witnesses,
                         formatted_witnesses: text_formatted_witnesses,
                         text: text,
                         id: context + '_' + i,
                         overtext_witnesses: overtext_witnesses,
                         overtext_page_name: overtext_page_name,
                         last_wit: last_over_wit,
                         i: i,
                        }
                    );
                }
            }
        }
    }

    var verse_number_normalised;
    if (verse_number_from_json == "Rubric") {
        verse_number_normalised = "R";
    } else {
        verse_number_normalised = verse_number_from_json / 100;
    }

    var variant_html = variant_template(variants);

    if (variants.length != 0) {
        $("#variants").append('<span class="variant_number"><strong>' + verse_number_normalised + ".</strong></span> ");
    }

    $("#variants").append(variant_html);
    $("#variants").append(" ");

    params = get_params(location.search);

    var html = overtext_template({blocks: output_readings,
                                  real_variants: real_variants,
                                  verse_num: verse_number_from_json});
    if (verse_number_from_json == 'Rubric') {
        $("#apparatus").append('<span class="chapter">' + document.getElementById('chapter').value + "</strong> ");
    } else {
        $("#apparatus").append("<sub>" + verse_number_normalised + "</sub> ");
    }
    $("#apparatus").append(html);
    $("#apparatus").append(" ");

    $("span.overtext").mouseover(function() {
    $( "span.variant" ).removeClass('hover');
        $( "span.overtext" ).removeClass('hover');
    var ovi_id = $(this)[0].id;
    var variant = $( "span.variant#" + ovi_id);
    variant.addClass('hover');
        var overtext_place = $( "span.overtext#" + ovi_id);
        if (overtext_place.has('span.critical_marker').length) {
            overtext_place.addClass('hover');
        }
    });

    $("span.variant").mouseover(function() {
    $( "span.variant" ).removeClass('hover');
        $( "span.overtext" ).removeClass('hover');
    var ovi_id = $(this)[0].id;
    var variant = $( "span.variant#" + ovi_id);
    variant.addClass('hover');
        var overtext_place = $( "span.overtext#" + ovi_id);
        if (overtext_place.has('span.critical_marker').length) {
            overtext_place.addClass('hover');
        }
    });
};

$(document).ready(function() {
    var params;
    params = get_params(location.search);
    $('#context').html(document.getElementById('chapter').value);

    function sleepFor( sleepDuration ){
        var now = new Date().getTime();
        while(new Date().getTime() < now + sleepDuration){ /* do nothing */ }
    }

    Handlebars.registerHelper('ifIn', function(elem, list, options) {
        if(list.indexOf(elem) > -1) {
            return options.fn(this);
        }
        return options.inverse(this);
    });

    VARIANT_NUMBER = -1;

    Handlebars.registerHelper("counter", function (index){
        VARIANT_NUMBER += 1;
        return VARIANT_NUMBER;
    });

    var chapter_name, collation_length, block_names, i, verse_name,
        block_name, verse_num, json_url, success_callback;

    var overtext_template, variant_template;

    overtext_template = Handlebars.compile($("#overtext-template").html());
    variant_template = Handlebars.compile($("#variant-template").html());

    chapter_name = document.getElementById('chapter').value;
    collation_length = COLLATION_LIST[chapter_name].length;
    block_names = new Array(collation_length);
    /* Make the list of block name files */
    for (i = 0; i < collation_length; i+=1) {
        verse_name = COLLATION_LIST[chapter_name][i];
        block_name = 'D' + chapter_name + 'S' + verse_name;
        block_names[i] = block_name;
    }

    success_callback = function(data) {
                process_data(data, overtext_template, variant_template);
            }
    for (verse_num = 0; verse_num < collation_length; verse_num+=1) {
        block_name = block_names[verse_num];
        json_url = document.getElementById('collations_path').value + '/' + block_name + ".json"

        $.ajax({
            url: json_url,
            dataType: 'json',
            async: false,
            success: success_callback
        });
    }
    save_text();
});
