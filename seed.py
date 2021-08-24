"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Listing

db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/listings.csv') as listings:
    db.session.bulk_insert_mappings(Listing, DictReader(listings))

db.session.commit()