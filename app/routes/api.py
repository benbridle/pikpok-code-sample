from app import app
from flask import jsonify, request, Blueprint
from app.models import *
from app import db
from app import exceptions
import sqlalchemy


api = Blueprint("api", __name__)


def assert_request_body():
    if request.json is None:
        raise exceptions.MissingBodyError()


def get_body_field(field_name):
    assert_request_body()
    field = request.json.get(field_name)
    if field is None:
        raise exceptions.MissingFieldError(field_name)
    return field


def get_body_fields(*field_names):
    assert_request_body()
    return {name: get_body_field(name) for name in field_names}


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.flush()
        return instance


@api.route("/")
def index():
    return jsonify("Doctrine API")


@api.route("/account/", methods=["GET"])
def get_accounts_metadata():
    accounts_info = {
        "count": db.session.query(Account).count(),
        "accounts": [get_account(account.id).get_json() for account in Account.query.all()],
    }
    return jsonify(accounts_info)


@api.route("/account/", methods=["POST"])
def create_account():
    email_address = get_body_field("email_address")
    email_address = get_or_create(EmailAddress, email_address=email_address)
    account = Account(email_address=email_address)
    db.session.add(account)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise exceptions.ResourceAlreadyExistsError("An account with this email address already exists.")
    return get_account(account.id)


@api.route("/account/<int:account_id>", methods=["GET"])
def get_account(account_id):
    account = Account.query.get(account_id)
    if account is None:
        raise exceptions.ResourceNotFoundError("An account with this ID was not found.")
    account_info = {
        "id": account.id,
        "email_address": str(account.email_address),
    }
    return jsonify(account_info)


@api.route("/profile/", methods=["GET"])
def get_profiles_metadata():
    profiles_info = {
        "count": db.session.query(Profile).count(),
        "profiles": [get_profile(profile.id).get_json() for profile in Profile.query.all()],
    }
    return jsonify(profiles_info)


@api.route("/profile/", methods=["POST"])
def create_profile():
    name = get_body_field("name")
    picture = get_body_field("picture")
    account_id = get_body_field("account_id")
    try:
        picture = int(picture)
    except ValueError:
        raise exceptions.MalformedFieldError("The 'picture' field must be an integer.")
    picture_bytes = picture.to_bytes(16, byteorder="big")
    account = Account.query.get(account_id)
    if account is None:
        raise exceptions.ResourceNotFoundError("An account with this ID was not found.")
    profile = Profile(account=account, picture=picture_bytes, name=name)
    db.session.add(profile)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if e.orig.args[0] == 1062 and ".name" in e.orig.args[1]:
            raise exceptions.ResourceAlreadyExistsError("A profile with the chosen name already exists.")
    return get_profile(profile.id)


@api.route("/profile/<int:profile_id>", methods=["GET"])
def get_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile is None:
        raise exceptions.ResourceNotFoundError("A profile with this ID was not found.")
    profile_info = {
        "id": profile.id,
        "name": profile.name,
        "picture": int.from_bytes(profile.picture, byteorder="big"),
        "account": get_account(profile.account_id).get_json(),
    }
    return jsonify(profile_info)


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
