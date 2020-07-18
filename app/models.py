import mmh3
import bcrypt
import string
import secrets
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import INTEGER, BINARY, DECIMAL, FLOAT
from app import db

Column = db.Column
Integer = db.Integer
String = db.String
Float = db.Float
ForeignKey = db.ForeignKey
DateTime = db.DateTime
Boolean = db.Boolean
Interval = db.Interval
relationship = db.relationship
UnsignedInt = INTEGER(unsigned=True)
UnsignedFloat = FLOAT(unsigned=True)


def Decimal(integer_places, decimal_places, **kwargs):
    return DECIMAL(precision=(integer_places + decimal_places), scale=decimal_places, **kwargs)


def UnsignedDecimal(integer_places, decimal_places, **kwargs):
    kwargs["unsigned"] = True
    return Decimal(integer_places, decimal_places, **kwargs)


class Account(db.Model):
    """An account is used to sign in to Doctrine, and contains all user information
    and credentials."""

    __tablename__ = "account"

    def __init__(self, email_address, password):
        # Generate password hash
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        super().__init__(email_address=email_address, password_hash=password_hash)

    def _asdict(self):
        account_info = {
            "id": self.id,
            "email_address": str(self.email_address),
            "creation_time": self.creation_time.replace(tzinfo=timezone.utc).isoformat(),
        }
        return account_info

    id = Column(UnsignedInt, primary_key=True)
    email_address_id = Column(UnsignedInt, ForeignKey("email_address.id"), nullable=False, unique=True)
    email_address = relationship("EmailAddress")
    password_hash = Column(BINARY(60), nullable=False)
    is_developer = Column(Boolean, nullable=False, default=False)
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Account '{self.email_address}'>"


class AccessToken(db.Model):
    """Used to authenticate the actions of a user without sending their credentials."""

    __tablename__ = "access_token"

    def generate_access_token(self):
        url_safe_characters = string.ascii_letters + "_-.~"
        while True:
            token = "".join([secrets.choice(url_safe_characters) for _ in range(64)])
            # Enforce token uniqueness
            if db.session.query(AccessToken).filter_by(token=token).count() == 0:
                return token

    def is_expired(self):
        return datetime.utcnow() > self.creation_time + self.duration

    id = Column(UnsignedInt, primary_key=True)
    account_id = Column(UnsignedInt, ForeignKey("account.id"), nullable=False)
    account = relationship("Account")
    token = Column(String(64), nullable=False, unique=True, default=generate_access_token)
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration = Column(Interval, nullable=False)

    def __repr__(self):
        return f"<AuthenticationToken #{self.id}>"

    def __str__(self):
        return self.token


class EmailAddress(db.Model):
    """Email addresses are normalised in order for uniqueness to be enforced."""

    __tablename__ = "email_address"

    def __init__(self, email_address):
        # Generate hash from the email address automatically
        email_hash = mmh3.hash128(email_address)
        email_hash = email_hash.to_bytes(16, byteorder="big")
        super().__init__(hash=email_hash, email_address=email_address)

    id = Column(UnsignedInt, primary_key=True)
    hash = Column(BINARY(16), nullable=False, unique=True)
    email_address = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<EmailAddress '{self.email_address}'>"

    def __str__(self):
        return self.email_address


class Profile(db.Model):
    """A profile is a single person in-game. One account can have multiple profiles,
    so that players don't need to create multiple accounts if they want to have
    multiple in-game characters."""

    __tablename__ = "profile"

    id = Column(UnsignedInt, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    picture = Column(BINARY(128), nullable=False)
    account_id = Column(UnsignedInt, ForeignKey("account.id"), nullable=False)
    account = relationship("Account")
    entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False, unique=True)
    entity = relationship("Entity")
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def _asdict(self):
        profile_info = {
            "id": self.id,
            "name": self.name,
            "picture": int.from_bytes(self.picture, byteorder="big"),
            "account": self.account._asdict(),
            "entity": self.entity._asdict(),
            "creation_time": self.creation_time.replace(tzinfo=timezone.utc).isoformat(),
        }
        return profile_info

    def __repr__(self):
        return f"<Profile '{self.name}'>"


class Team(db.Model):
    """A team of players working together. Can own assets and money."""

    __tablename__ = "team"
    id = Column(UnsignedInt, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    picture = Column(BINARY(128), nullable=False)
    entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False, unique=True)
    entity = relationship("Entity")

    def __repr__(self):
        return f"<Team '{self.name}'>"


class Entity(db.Model):
    """A 'legal person' who can own assets, either a profile or a team."""

    def _asdict(self):
        entity_info = {
            "id": self.id,
        }
        return entity_info

    __tablename__ = "entity"
    id = Column(UnsignedInt, primary_key=True)


class Inventory(db.Model):
    """A container for assets."""

    __tablename__ = "inventory"
    id = Column(UnsignedInt, primary_key=True)
    quantity_limit = Column(UnsignedInt)
    volume_limit = Column(UnsignedFloat)

    def __repr__(self):
        return f"<Inventory #{self.id}>"


class Asset(db.Model):
    """An ownable item, owned by an entity."""

    __tablename__ = "asset"
    id = Column(UnsignedInt, primary_key=True)
    entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False)
    entity = relationship("Entity")

    def __repr__(self):
        return f"<Asset #{self.id}>"


class Resource(db.Model):
    """An asset as stored in an inventory, holds all the inventory-related attributes of an asset."""

    __tablename__ = "resource"
    id = Column(UnsignedInt, primary_key=True)
    asset_id = Column(UnsignedInt, ForeignKey("asset.id"), nullable=False, unique=True)
    asset = relationship("Asset")
    inventory_id = Column(UnsignedInt, ForeignKey("inventory.id"), nullable=False)
    inventory = relationship("Inventory")
    # if resource_type_id is NULL, the inventory characteristics of the asset
    # are obtained from a world_entity linked to the asset. This is the case for
    # complex assets, such as vehicles.
    resource_type_id = Column(UnsignedInt, ForeignKey("resource_type.id"), nullable=True)
    resource_type = relationship("ResourceType")

    def __repr__(self):
        return f"<Resource #{self.id} {self.resource_type.name}>"


class ResourceType(db.Model):
    """A single 'class' of asset (eg. iron ore, improved heatsink, light tyre)"""

    __tablename__ = "resource_type"
    id = Column(UnsignedInt, primary_key=True)
    mass = Column(UnsignedDecimal(10, 3), nullable=False)
    volume = Column(UnsignedDecimal(10, 3), nullable=False)
    name = Column(String(32), nullable=False, unique=True)

    def __repr__(self):
        return f"<ResourceType '{self.name}'>"


class Dome(db.Model):
    """A dome is a 'region' of the world. The world is made up of a network of biodomes."""

    __tablename__ = "dome"

    id = Column(UnsignedInt, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    diameter = Column(UnsignedInt, nullable=False)  # Meters
    world_location_x = Column(Integer, nullable=False)
    world_location_y = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Dome '{self.name}'>"


class DomeConnection(db.Model):
    """A tunnel connecting two biodomes to each other."""

    __tablename__ = "dome_connection"

    dome_id_1 = Column(UnsignedInt, ForeignKey("dome.id"), primary_key=True)
    dome_id_2 = Column(UnsignedInt, ForeignKey("dome.id"), primary_key=True)
    dome_1 = relationship("Dome", foreign_keys=dome_id_1)
    dome_2 = relationship("Dome", foreign_keys=dome_id_2)

    def __repr__(self):
        return f"<DomeConnection '{self.dome_1.name}-{self.dome_2.name}'>"


class WorldEntity(db.Model):
    """An asset as a 3D object physically in the game world."""

    __tablename__ = "world_entity"
    id = Column(UnsignedInt, primary_key=True)
    location_dome_id = Column(UnsignedInt, ForeignKey("dome.id"), nullable=False)
    location_dome = relationship("Dome")
    location_x = Column(Integer, nullable=False)
    location_y = Column(Integer, nullable=False)
    heading = Column(Float, nullable=False, default=0)  # In radians

    def __repr__(self):
        return f"<WorldEntity '{self.name}'>"


class Wallet(db.Model):
    """Stores in-game money."""

    __tablename__ = "wallet"
    id = Column(UnsignedInt, primary_key=True)
    value = Column(UnsignedDecimal(12, 2), nullable=False)
    entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False)
    entity = relationship("Entity")

    def __repr__(self):
        return f"<Wallet #{self.id}>"


# Logging tables


class TransactionEvent:
    """A transaction of assets and/or money between two entities. Can tie
    together multiple financial and asset exchanges."""

    __tablename__ = "transaction_event"

    id = Column(UnsignedInt, primary_key=True)
    transaction_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<TransactionEvent #{self.id}>"


class FinancialTransaction:
    """Financial exchange component of a transaction."""

    __tablename__ = "financial_transaction"

    id = Column(UnsignedInt, primary_key=True)
    value = Column(Decimal(12, 2), nullable=False)
    sending_wallet_id = Column(UnsignedInt, ForeignKey("wallet.id"), nullable=False)
    sending_wallet = relationship("Wallet", foreign_keys=sending_wallet_id)
    receiving_wallet_id = Column(UnsignedInt, ForeignKey("wallet.id"), nullable=False)
    receiving_wallet = relationship("Wallet", foreign_keys=receiving_wallet_id)
    transaction_event_id = Column(UnsignedInt, ForeignKey("transaction_event.id"), nullable=False)
    transaction_event = relationship("TransactionEvent")

    def __repr__(self):
        return f"<FinancialTransaction #{self.id}>"


class AssetTransaction:
    """Asset exchange component of a transaction."""

    __tablename__ = "asset_transaction"

    id = Column(UnsignedInt, primary_key=True)
    asset_id = Column(UnsignedInt, ForeignKey("asset.id"), nullable=False)
    asset = relationship("Asset")
    sending_entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False)
    sending_entity = relationship("Entity", foreign_keys=sending_entity_id)
    receiving_entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False)
    receiving_entity = relationship("Entity", foreign_keys=receiving_entity_id)
    transaction_event_id = Column(UnsignedInt, ForeignKey("transaction_event.id"), nullable=False)
    transaction_event = relationship("TransactionEvent")

    def __repr__(self):
        return f"<AssetTransaction #{self.id}>"


class AccountSignInEvent:
    """Logs the time an account was signed in to."""

    __tablename__ = "account_sign_in_event"

    id = Column(UnsignedInt, primary_key=True)
    account_id = Column(UnsignedInt, ForeignKey("account.id"), nullable=False)
    account = relationship("Account")
    sign_in_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<AccountSignInEvent #{self.id}>"
