import csv
from random import sample, choice
from itertools import permutations
from faker import Faker
from helpers import get_random_datetime
import json
from my_secrets import S3_SMALL_BUCKET, S3_LARGE_BUCKET, S3_KEY, S3_SECRET
import boto3

USERS_CSV_HEADERS = ['email', 'username', 'password', 'phone', 'first_name', 'last_name']
MESSAGES_CSV_HEADERS = ['text', 'to_user_id', 'from_user_id', 'timestamp']
LISTINGS_CSV_HEADERS = ['address', 'title', 'details', 'host_id', 'price']
LISTING_PHOTOS_CSV_HEADERS = ['listing_id', 'small_photo_url', 'large_photo_url']

MAX_MESSAGE_LENGTH = 150
MAX_TITLE_LENGTH = 20
MAX_DETAILS_LENGTH = 150

NUM_USERS = 30
NUM_MESSAGES = 5000
NUM_LISTINGS = 50
NUM_LISTING_PHOTOS = 600

fake = Faker('en_US')

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

small_images_response = s3.list_objects(Bucket=S3_SMALL_BUCKET)
small_images = small_images_response['Contents']
large_images_response = s3.list_objects(Bucket=S3_LARGE_BUCKET)
large_images = large_images_response['Contents']

with open('generator/users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password='$2b$12$kHeUjJysDxb9Spvj8IaAPumKaZMsGxgewGGLsdQcPDFzbbQ6P2Gae',
            phone=fake.unique.phone_number()
        ))

with open('generator/messages.csv', 'w') as messages_csv:
    messages_writer = csv.DictWriter(messages_csv, fieldnames=MESSAGES_CSV_HEADERS)
    messages_writer.writeheader()
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))
    random_pairs = [choice(all_pairs) for n in range(NUM_MESSAGES)]

    for to_user_id, from_user_id in random_pairs:
        messages_writer.writerow(dict(
            text=fake.paragraph()[:MAX_MESSAGE_LENGTH],
            timestamp=get_random_datetime(),
            to_user_id=to_user_id,
            from_user_id=from_user_id,
        ))

with open('generator/listings.csv', 'w') as listings_csv: 
    listings_writer = csv.DictWriter(listings_csv, fieldnames=LISTINGS_CSV_HEADERS)
    listings_writer.writeheader()

    for i in range(NUM_LISTINGS): 
        listings_writer.writerow(dict(
            price=fake.random_int(min=0, max=500),
            host_id=fake.random_int(min=1, max=NUM_USERS),
            details=fake.paragraph()[:MAX_DETAILS_LENGTH],
            title=fake.sentence(nb_words=3),
            address=fake.address(),
        ))

with open('generator/listing_photos.csv', 'w') as listing_photos_csv: 
    listing_photos_writer = csv.DictWriter(listing_photos_csv, fieldnames=LISTING_PHOTOS_CSV_HEADERS)
    listing_photos_writer.writeheader()
    for i in range(NUM_LISTING_PHOTOS): 
        listing_photos_writer.writerow(dict(
            listing_id=fake.random_int(min=1, max=NUM_LISTINGS),
            small_photo_url = 'http://{}.s3.amazonaws.com/'.format(S3_SMALL_BUCKET) + choice(small_images)['Key'],
            large_photo_url = 'http://{}.s3.amazonaws.com/'.format(S3_LARGE_BUCKET) + choice(large_images)['Key'],
        ))