""" SQLAlchemy models for ShareBnB. """

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class User(db.Model): 
    """ User in the system. """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    phone = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    listings = db.relationship(
        'Listing',
        backref='host'
    )

    incoming_messages = db.relationship(
        "Message",
        backref='to_user'
    )

    outgoing_messages = db.relationship(
        "Message",
        backref='from_user'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


class Message(db.Model):
    """A private message between users."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    to_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    from_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    def __repr__(self):
        return f"<Message #{self.id}: {self.text} by {self.user_id}>"


class Listing(db.Model):
    """A listing in the system."""

    __tablename__ = "listings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    price = db.Column(
        db.Integer,
        nullable=False,
    )

    details = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    host = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )


class ListingPhoto(db.Model):
    """A photo within a listing."""

    __tablename__ = "listing_photos"

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
    )

    listing_id = db.Column(
        db.Integer, 
        db.ForeignKey('listings.id', ondelete='CASCADE'),
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    listing = db.relationship(
        'Listing',
        backref='photos'
    )


