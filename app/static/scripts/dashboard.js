function get_account_information() {
    send_request("/api/accounts/" + get_account_id(), get_account_information_callback);
}

function get_account_information_callback(response) {
    document.getElementById("account-email").innerHTML = response.response.email_address;
    var created_on = new Date(response.response.creation_time)
    var date_options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById("account-created-on").innerHTML = created_on.toLocaleDateString(undefined, date_options);
    document.getElementById("account-is-developer").innerHTML = response.response.is_developer;
    response.response.profiles.forEach(profile => {
        add_profile_card(profile.name, profile.entity.wallet.value);
    });
}

function add_profile_card(name, money, picture) {
    var card_template = document.getElementById("toolbox").getElementsByClassName("profile-card")[0];
    var reference_card = document.getElementById("create-profile");
    var new_card = card_template.cloneNode(true);
    new_card.getElementsByTagName("h1")[0].innerHTML = name;
    new_card.getElementsByTagName("h2")[0].innerHTML = "$" + money.toFixed(2);;
    document.getElementById("profile-container").insertBefore(new_card, reference_card);
}

function create_profile(name, picture) {
    body_data = {
        "account_id": get_account_id(),
        "name": name,
        "picture": picture,
    }
    send_request("/api/profiles/", create_profile_callback, body_data);
}

function create_profile_callback(response) {
    var profile = response.response;
    console.log(profile);
    add_profile_card(profile.name, profile.entity.wallet.value, profile.picture);
}