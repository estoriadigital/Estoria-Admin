var COLLATION = (function () {

    // var read_params = function () {
    //     var params = {};
    //     if (location.search) {
    //         var parts = location.search.substring(1).split('&');
    //
    //         for (var i = 0; i < parts.length; i++) {
    //             var nv = parts[i].split('=');
    //             if (!nv[0]) continue;
    //             params[nv[0]] = nv[1] || true;
    //         }
    //     }
    //     return params;
    // };



    var read_JSON_file = function (path, callback) {
        var httpRequest = new XMLHttpRequest();
        httpRequest.onreadystatechange = function() {
            if (httpRequest.readyState === 4) {
                if (httpRequest.status === 200) {
                    var data = JSON.parse(httpRequest.responseText);
                    if (callback) callback(data);
                }
            }
        };
        httpRequest.open('GET', path);
        httpRequest.send();
    };

    return {
        read_JSON_file: read_JSON_file,
        // read_params: read_params
    };

})();
