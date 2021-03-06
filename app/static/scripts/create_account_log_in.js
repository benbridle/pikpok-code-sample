function show_loader() {
    document.getElementById("loader").classList.remove("gone");
    document.getElementById("submit-button").classList.add("gone");
};

function hide_loader() {
    document.getElementById("loader").classList.add("gone");
    document.getElementById("submit-button").classList.remove("gone");
};

function create_account(email_address, password) {
    var request_body = { "email_address": email_address, "password": password };
    reset_error_state();
    show_loader();
    send_request("/api/accounts/", create_account_callback, request_body);
}

function create_account_callback(response) {
    hide_loader();
    switch (response.status) {
        case 201:
            document.getElementById("create-account-card").classList.add("gone");
            document.getElementById("continue-card").classList.remove("gone");
            break;
        case 409:
            set_error_message("Email address already in use");
            document.getElementById("email").classList.add("error")
            break;
        case 500:
            set_error_message("An error has occurred");
            break;
    }
}

function create_account_continue() {
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    document.getElementById("continue-loader").classList.remove("gone");
    document.getElementById("continue-button").classList.add("gone");
    log_in(email, password);
}

function log_in(email_address, password) {
    var request_body = { "email_address": email_address, "password": password }
    reset_error_state();
    show_loader();
    send_request("/api/login", log_in_callback, request_body);
}

function log_in_callback(response) {
    hide_loader();
    switch (response.status) {
        case 200:
            localStorage.setItem("access_token", response.response.token);
            localStorage.setItem("account_id", response.response.account.id);
            window.location.replace('/dashboard');
            break;
        case 403:
            set_error_message("Invalid credentials");
            document.getElementById("email").classList.add("error");
            document.getElementById("password").classList.add("error");
            break;
        case 500:
            set_error_message("An error has occurred")
            console.log(response);
            break;
    }
}

function set_error_message(message) {
    var error_message = document.getElementById("error-message");
    error_message.classList.remove("hidden");
    error_message.innerHTML = message;
}


function reset_error_state() {
    document.getElementById("email").classList.remove("error");
    document.getElementById("password").classList.remove("error");
    try { document.getElementById("confirm-password").classList.remove("error"); } catch (e) {}
    document.getElementById("error-message").classList.add("hidden");
}

// Add letter spacing when entering a password. This is done because spacing
// looks good applied to password dots, but looks bad applied to hint text.
function passwordUpdate(event) {
    reset_error_state();
    if (event.target.value.length == 0) {
        event.target.style.letterSpacing = "0px";
    } else {
        event.target.style.letterSpacing = "3px";
    }
}