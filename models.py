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
        foreign_keys="Message.to_user_id",
        backref="to_user"
    )

    outgoing_messages = db.relationship(
        "Message",
        foreign_keys="Message.from_user_id",
        backref="from_user"
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, {self.id}, >"

    @classmethod
    def signup(cls, username, email, password, first_name, last_name, phone):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    def serialize(self): 
        """Serializes self to dictionary."""

        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
        }


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

    def serialize(self):
        return {
            'id':self.id,
            'text':self.text,
            'timestamp':self.timestamp,
            'to_user_id':self.to_user_id,
            'from_user_id':self.from_user_id,
        }



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

    host_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    def serialize(self): 
        """ Serializes class instance to dictionary. """

        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "details": self.details,
            "address": self.address,
            "host_id": self.host_id,
            "photos": [photo.serialize() for photo in self.photos],
        }




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


    def serialize(self): 
        """Serializes instance."""

        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "url": self.url,
        }