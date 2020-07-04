from app import db
from sqlalchemy.dialects.mysql import INTEGER, BINARY, DECIMAL
import mmh3

Column = db.Column
Integer = db.Integer
String = db.String
Float = db.Float
ForeignKey = db.ForeignKey
relationship = db.relationship
UnsignedInt = INTEGER(unsigned=True)


def UnsignedDecimal(integer_places, decimal_places):
    return DECIMAL(precision=(integer_places + decimal_places), scale=decimal_places, unsigned=True)


class Account(db.Model):
    __tablename__ = "account"

    id = Column(UnsignedInt, primary_key=True, nullable=False)
    email_address_id = Column(UnsignedInt, ForeignKey("email_address.id"), nullable=False, unique=True)
    email_address = relationship("EmailAddress")

    def __repr__(self):
        return f"<Account '{self.email_address}'>"


class EmailAddress(db.Model):
    __tablename__ = "email_address"

    def __init__(self, email_address):
        """Generates the hash from the email address automatically"""
        email_hash = mmh3.hash128(email_address)
        email_hash = email_hash.to_bytes(16, byteorder="big")
        super().__init__(hash=email_hash, email_address=email_address)

    id = Column(UnsignedInt, primary_key=True, nullable=False)
    hash = Column(BINARY(16), nullable=False, unique=True)
    email_address = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<EmailAddress '{self.email_address}'>"

    def __str__(self):
        return self.email_address


class Profile(db.Model):
    __tablename__ = "profile"

    id = Column(UnsignedInt, primary_key=True, nullable=False)
    account_id = Column(UnsignedInt, ForeignKey("account.id"), nullable=False)
    account = relationship("Account")
    name = Column(String(32), unique=True, nullable=False)
    picture = Column(BINARY(128), nullable=False)

    def __repr__(self):
        return f"<Profile '{self.name}'>"


class Dome(db.Model):
    __tablename__ = "dome"

    id = Column(UnsignedInt, primary_key=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False)
    diameter = Column(UnsignedInt, nullable=False)
    world_location_x = Column(Float, nullable=False)
    world_location_y = Column(Float, nullable=False)
    base_wind_speed = Column(Float, nullable=True)  # TODO: Make these not nullable in the future
    base_ambient_temperature = Column(Float, nullable=True)
    operator_entity_id = Column(UnsignedInt, ForeignKey("entity.id"))
    operator = relationship("Entity")

    def __repr__(self):
        return f"<Dome '{self.name}'>"


class DomeConnection(db.Model):
    __tablename__ = "dome_connection"

    dome_id_1 = Column(UnsignedInt, ForeignKey("dome.id"), nullable=False, primary_key=True)
    dome_id_2 = Column(UnsignedInt, ForeignKey("dome.id"), nullable=False, primary_key=True)
    dome_1 = relationship("Dome", foreign_keys=dome_id_1)
    dome_2 = relationship("Dome", foreign_keys=dome_id_2)

    def __repr__(self):
        return f"<DomeConnection '{self.dome_1.name}-{self.dome_2.name}'>"


class Entity(db.Model):
    __tablename__ = "entity"
    id = Column(UnsignedInt, primary_key=True, nullable=False)


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    quantity_limit = Column(UnsignedInt)
    volume_limit = Column(UnsignedInt)

    def __repr__(self):
        return f"<Inventory #{self.id}>"


class Resource(db.Model):
    __tablename__ = "resource"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    asset_id = Column(UnsignedInt, ForeignKey("asset.id"), nullable=False)
    inventory_id = Column(UnsignedInt, ForeignKey("inventory.id"), nullable=False)
    resource_type_id = Column(UnsignedInt, ForeignKey("resource_type.id"), nullable=False)
    asset = relationship("Asset")
    inventory = relationship("Inventory")
    resource_type = relationship("ResourceType")

    def __repr__(self):
        return f"<Resource #{self.id} {self.resource_type.name}>"


class ResourceType(db.Model):
    __tablename__ = "resource_type"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    mass = Column(UnsignedDecimal(10, 3), nullable=False)
    volume = Column(UnsignedDecimal(10, 3), nullable=False)
    name = Column(String(32), nullable=False, unique=True)

    def __repr__(self):
        return f"<ResourceType '{self.name}'>"


class Asset(db.Model):
    __tablename__ = "asset"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    entity_id = Column(UnsignedInt, ForeignKey("entity.id"), nullable=False)
    entity = relationship("Entity")

    def __repr__(self):
        return f"<Asset #{self.id}>"


class Team(db.Model):
    __tablename__ = "team"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)
    picture = Column(
        BINARY(128), nullable=False
    )  # TODO: Make not nullable once picture generation infrastructure in in place

    def __repr__(self):
        return f"<Team '{self.name}'>"


class Wallet(db.Model):
    __tablename__ = "wallet"
    id = Column(UnsignedInt, primary_key=True, nullable=False)
    value = Column(UnsignedDecimal(12, 2), nullable=False)

    def __repr__(self):
        return f"<Wallet #{self.id}>"

