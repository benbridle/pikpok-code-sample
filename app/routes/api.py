import sqlalchemy
import mmh3
from datetime import timedelta
from flask import jsonify, request, Blueprint
from app import db
from app.models import *
from app import exceptions
from app.modules.profile_image import generate_profile_image, ProfileImage


api = Blueprint("api", __name__)


def assert_request_body():
    """Ensure the request has body data."""
    if request.json is None:
        raise exceptions.MissingBodyError()


def get_body_field(field_name, field_type=None):
    """Ensure the request has a specific body field, and return it."""
    assert_request_body()
    field = request.json.get(field_name)
    if field is None:
        raise exceptions.MissingFieldError(field_name)
    if field_type is not None:
        if not isinstance(field, field_type):
            raise exceptions.MalformedFieldError(f"The '{field_name}' field must be of type '{field_type.__name__}'.")
    return field


def get_body_fields(*field_names):
    """Ensure the request has all specified body fields, and return them."""
    assert_request_body()
    return {name: get_body_field(name) for name in field_names}


def get_or_create_record(model, **kwargs):
    """Fetch a database record, creating it first if it doesn't exist."""
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.flush()
        return instance


def get_current_account():
    """Returns the account associated with the current request."""
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise exceptions.MissingHeaderError("Authorization")
    if not authorization.startswith("Bearer "):
        raise exceptions.MalformedHeaderError("Authorization header content must start with 'Bearer '.")
    token_string = authorization[len("Bearer ") :]
    # Check if the access token exists and is not expired
    try:
        token = AccessToken.query.filter_by(token=token_string).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
    if token.is_expired():
        raise exceptions.ExpiredTokenError
    return token.account


def restrict_access(authorized_account_id=None, error_message=None):
    """Restrict access to only developers and the specified account."""
    try:
        current_account = get_current_account()
    except exceptions.MissingHeaderError:
        raise exceptions.NoAuthorizationSuppliedError
    if current_account is None:
        raise exceptions.UnauthorizedAccessError(error_message)
    if current_account.is_developer:
        return
    if authorized_account_id is None:
        raise exceptions.UnauthorizedAccessError(error_message)
    if current_account.id == authorized_account_id:
        return
    raise exceptions.UnauthorizedAccessError(error_message)


@api.route("/")
def index():
    return jsonify("Doctrine API")


@api.route("/generators/profile_image")
def generate_random_profile_image():
    """Get a randomly generated profile image as a Base64-encoded string."""
    return jsonify({"image": generate_profile_image().to_base64_string()})


@api.route("/login", methods=["POST"])
def login():
    # Find the account matching the given email address
    password = get_body_field("password")
    email_address = get_body_field("email_address")
    email_hash = mmh3.hash128(email_address)
    email_hash = email_hash.to_bytes(16, byteorder="big")
    try:
        email_address = EmailAddress.query.filter_by(hash=email_hash).one()
        account = Account.query.filter_by(email_address=email_address).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise exceptions.InvalidCredentialsError
    # Test that the password matches the hashed account password
    if not bcrypt.checkpw(password.encode("utf-8"), account.password_hash):
        raise exceptions.InvalidCredentialsError
    # Generate and return an access token
    token = AccessToken(account=account, duration=timedelta(hours=24))
    db.session.add(token)
    db.session.commit()
    return jsonify({"token": str(token), "account": account,})


@api.route("/accounts/")
def get_accounts_metadata():
    restrict_access()
    accounts_info = {
        "count": db.session.query(Account).count(),
        "accounts": [account for account in Account.query.all()],
    }
    return jsonify(accounts_info)


@api.route("/accounts/", methods=["POST"])
def create_account():
    password = get_body_field("password")
    email_address = get_body_field("email_address")
    email_address = get_or_create_record(EmailAddress, email_address=email_address)
    account = Account(email_address=email_address, password=password)
    db.session.add(account)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise exceptions.ResourceAlreadyExistsError("An account with this email address already exists.")
    return jsonify(account), 201


@api.route("/accounts/<int:account_id>")
def get_account(account_id):
    restrict_access(account_id)
    account = Account.query.get(account_id)
    if account is None:
        raise exceptions.ResourceNotFoundError("An account with this ID was not found.")
    return jsonify(account)


@api.route("/profiles/")
def get_profiles_metadata():
    restrict_access()
    profiles_info = {
        "count": db.session.query(Profile).count(),
        "profiles": [profile._asdict() for profile in Profile.query.all()],
    }
    return jsonify(profiles_info)


@api.route("/profiles/", methods=["POST"])
def create_profile():
    account_id = get_body_field("account_id", field_type=int)
    restrict_access(account_id, "Only the owner of an account can create a profile for that account.")
    name = get_body_field("name")
    try:
        picture_string = get_body_field("picture", field_type=str)
        picture = ProfileImage.from_base64_string(picture_string)
    except exceptions.MissingFieldError:
        # If no picture is provided, generate one
        picture = generate_profile_image()
    picture_bytes = bytes(picture)

    account = Account.query.get(account_id)
    if account is None:
        raise exceptions.ResourceNotFoundError("An account with the specified ID was not found.")
    if not Profile.query.filter_by(name=name).count() == 0:
        raise exceptions.ResourceAlreadyExistsError("Another profile with the chosen name already exists.")

    # Create the profile
    entity = Entity()
    db.session.add(entity)
    profile = Profile(account=account, name=name, picture=picture_bytes, entity=entity)
    db.session.add(profile)
    db.session.commit()
    return jsonify(profile), 201


@api.route("/profiles/<int:profile_id>")
def get_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile is None:
        # If the user isn't a developer, return an UnauthorizedAccessError
        restrict_access()
        # If the user is a developer, return a more informative error
        raise exceptions.ResourceNotFoundError("A profile with this ID was not found.")
    restrict_access(profile.account.id)
    return jsonify(profile)


@api.errorhandler(exceptions.BaseError)
def base_error_handler(error):
    status_code = error.status_code or 500
    response = {"error": {"type": error.__class__.__name__, "message": error.message}}
    return jsonify(response), status_code


@api.errorhandler(NotImplementedError)
def not_implemented_handler(error):
    error.status_code = 500
    error.message = "Functionality not implemented"
    return base_error_handler(error)
