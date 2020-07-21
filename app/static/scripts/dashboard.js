function get_account_information() {
    send_request("/api/accounts/" + get_account_id(), get_account_information_callback);
}

function get_account_information_callback(response) {
    // If fetching account information failed (due to expired token or invalid stored
    // details), make user log in again.
    if (response.status != 200) {
        alert("Session expired, please log in again.");
        log_out(redirect_to = "/login");
        return;
    }
    // Write account information to list at the top of the page
    document.getElementById("account-email").innerHTML = response.response.email_address;
    var created_on = new Date(response.response.creation_time)
    var date_options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = created_on.toLocaleDateString(undefined, date_options);
    document.getElementById("account-created-on").innerHTML = date;
    document.getElementById("account-is-developer").innerHTML = response.response.is_developer;

    // Create a profile card for each profile associated with the account
    response.response.profiles.forEach(profile => {
        add_profile_card(profile.name, profile.entity.wallet.value, profile.picture);
    });
}

function add_profile_card(name, money, picture) {
    var card_template = document.getElementById("toolbox").getElementsByClassName("profile-card")[0];
    var new_card = card_template.cloneNode(true);

    // Set information values on new card
    new_card.getElementsByTagName("h1")[0].innerHTML = name;
    new_card.getElementsByTagName("h2")[0].innerHTML = "$" + money.toFixed(2);

    // Set profile picture on new card
    var canvas = new_card.getElementsByTagName("canvas")[0];
    initialise_profile_image(canvas);
    canvas.profile_image.from_base64(picture);

    // Add new card to profile card container
    var reference_card = document.getElementById("create-profile");
    document.getElementById("profile-container").insertBefore(new_card, reference_card);
}

function randomise_new_profile_image() {
    // Fetch a new generated image for the profile image editor
    send_request("/api/generators/profile_image", randomise_new_profile_image_callback);
}

function randomise_new_profile_image_callback(response) {
    var generated_image = response.response.image;
    var profile_image_editor = document.getElementById("profile-image-editor");
    profile_image_editor.profile_image.from_base64(generated_image);
}

function show_create_profile_modal() {
    // Shows the modal to create a new profile
    var modal = document.getElementById("create-profile-modal")
    modal.classList.remove("gone");
    document.getElementById("fade-background").classList.remove("gone");
    var profile_image = document.getElementById("profile-image-editor").profile_image;
    profile_image.clear();
    randomise_new_profile_image();
}

function hide_create_profile_modal() {
    document.getElementById("create-profile-modal").classList.add("gone");
    document.getElementById("fade-background").classList.add("gone");
    document.getElementById("profile-name").value = "";
    reset_error_state();
}

function create_profile(name, picture) {
    // Create a new profile on the server
    show_loader();
    reset_error_state();
    body_data = {
        "account_id": get_account_id(),
        "name": name,
        "picture": picture,
    }
    send_request("/api/profiles/", create_profile_callback, body_data);
}

function create_profile_callback(response) {
    hide_loader();
    switch (response.status) {
        case 201:
            var profile = response.response;
            add_profile_card(profile.name, profile.entity.wallet.value, profile.picture);
            hide_create_profile_modal();
            break;
        case 409:
            set_error_message("Profile name already taken");
            document.getElementById("profile-name").classList.add("error")
            break;
        case 500:
            set_error_message("An error has occurred");
            console.log(response);
            break;
    }
}