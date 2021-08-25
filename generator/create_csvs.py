import csv
from random import sample, choice
from itertools import permutations
from faker import Faker
from helpers import get_random_datetime

USERS_CSV_HEADERS = ['email', 'username', 'password', 'phone', 'first_name', 'last_name']
MESSAGES_CSV_HEADERS = ['text', 'to_user_id', 'from_user_id', 'timestamp']
LISTINGS_CSV_HEADERS = ['address', 'title', 'details', 'host_id', 'price']
LISTING_PHOTOS_CSV_HEADERS = ['listing_id', 'url']

MAX_MESSAGE_LENGTH = 150
MAX_TITLE_LENGTH = 20
MAX_DETAILS_LENGTH = 150

NUM_USERS = 300
NUM_MESSAGES = 500
NUM_LISTINGS = 100
NUM_LISTING_PHOTOS = 500

fake = Faker('en_US')

image_urls = [
    f"https://randomuser.me/api/portraits/{kind}/{i}.jpg"
    for kind, count in [("lego", 10), ("men", 100), ("women", 100)]
    for i in range(count)
]

with open('generator/users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password='$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe',
            phone=fake.unique.phone_number()
        ))

with open('generator/messages.csv', 'w') as messages_csv:
    messages_writer = csv.DictWriter(messages_csv, fieldnames=MESSAGES_CSV_HEADERS)
    messages_writer.writeheader()
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))

    for to_user_id, from_user_id in sample(all_pairs, NUM_MESSAGES):
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
            title=fake.sentence(nb_words=5),
            address=fake.address(),
        ))

with open('generator/listing_photos.csv', 'w') as listing_photos_csv: 
    listing_photos_writer = csv.DictWriter(listing_photos_csv, fieldnames=LISTING_PHOTOS_CSV_HEADERS)
    listing_photos_writer.writeheader()
    for i in range(NUM_LISTING_PHOTOS): 
        listing_photos_writer.writerow(dict(
            listing_id=fake.random_int(min=1, max=NUM_LISTINGS),
            url=choice(image_urls)
        ))