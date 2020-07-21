function send_request(url, callback, body_data = null, method = null) {
    var request = new XMLHttpRequest();
    if (method === null) {
        if (body_data === null) {
            method = "GET";
        } else {
            method = "POST";
        }
    }

    request.onreadystatechange = function() {
        if (this.readyState == 4) { // state 4 means completed
            callback(this);
        }
    };

    request.responseType = "json"
    request.open(method, url);
    // Set Authorization header
    if (get_token() !== null) {
        request.setRequestHeader("Authorization", "Bearer " + get_token());
    }
    // Add request body data
    if (body_data !== null) {
        request.setRequestHeader("Content-Type", "application/json");
        body_data = JSON.stringify(body_data);
        request.send(body_data);
    } else {
        request.send();
    }
}

function get_token() {
    return localStorage.getItem("access_token");
}

function get_account_id() {
    return Number(localStorage.getItem("account_id"));
}

function log_out(redirect_to = "/") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("account_id");
    window.location.replace(redirect_to);
}