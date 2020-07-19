function get_account_information() {
    send_request("/api/accounts/" + get_account_id(), get_account_information_callback);
}

function get_account_information_callback(response) {
    // Write account information to list at the top of the page
    document.getElementById("account-email").innerHTML = response.response.email_address;
    var created_on = new Date(response.response.creation_time)
    var date_options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById("account-created-on").innerHTML = created_on.toLocaleDateString(undefined, date_options);
    document.getElementById("account-is-developer").innerHTML = response.response.is_developer;
    // Add a profile card for each profile associated with the account
    response.response.profiles.forEach(profile => {
        add_profile_card(profile.name, profile.entity.wallet.value, profile.picture);
    });
    initialise_profile_image(document.getElementById("new-profile-image"));
    initialise_palette();
}

function add_profile_card(name, money, picture) {
    var card_template = document.getElementById("toolbox").getElementsByClassName("profile-card")[0];
    var reference_card = document.getElementById("create-profile");
    var new_card = card_template.cloneNode(true);
    new_card.getElementsByTagName("h1")[0].innerHTML = name;
    new_card.getElementsByTagName("h2")[0].innerHTML = "$" + money.toFixed(2);
    var canvas = new_card.getElementsByTagName("canvas")[0];
    initialise_profile_image(canvas);
    canvas.profile_image.from_base64(picture);
    document.getElementById("profile-container").insertBefore(new_card, reference_card);
}

function randomise_new_profile_image() {
    // Fetch a new generated image for the profile image editor
    send_request("/api/generators/profile_image", randomise_new_profile_image_callback);
}

function randomise_new_profile_image_callback(response) {
    var modal = document.getElementById("create-profile-modal")
    var new_profile_image = modal.getElementsByClassName("profile-image")[0].profile_image;
    new_profile_image.from_base64(response.response.image)
    new_profile_image.render();
}

function show_create_profile_modal() {
    // Shows the modal to create a new profile
    var modal = document.getElementById("create-profile-modal")
    modal.classList.remove("gone");
    document.getElementById("fade-background").classList.remove("gone");
    var profile_image = modal.getElementsByClassName("profile-image")[0].profile_image;
    profile_image.clear();
    profile_image.render();
    randomise_new_profile_image();
}

function hide_create_profile_modal() {
    document.getElementById("create-profile-modal").classList.add("gone");
    document.getElementById("fade-background").classList.add("gone");
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
    // hide_loader();
    console.log(response);
    switch (response.status) {
        case 201:
    var profile = response.response;
            console.log(profile.entity.wallet.value);
    add_profile_card(profile.name, profile.entity.wallet.value, profile.picture);
            hide_create_profile_modal();
            break;
        case 409:
            set_error_message("Profile name already taken");
            document.getElementById("profile-name").classList.add("error")
            break;
        case 500:
            set_error_message("An error has occurred");
            break;
    }


}