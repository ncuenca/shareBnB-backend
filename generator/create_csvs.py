import csv
from random import choice, randint, sample
from itertools import permutations
import requests
from faker import Faker
from helpers import get_random_datetime

USERS_CSV_HEADERS = ['email', 'username', 'password', 'phone', 'first_name', 'last_name', 'is_admin']
MESSAGES_CSV_HEADERS = ['text', 'to_user', 'from_user', 'timestamp']
LISTINGS_CSV_HEADERS = ['photo_urls', 'address', 'title', 'details', 'host', 'price']

MAX_MESSAGE_LENGTH = 150
MAX_TITLE_LENGTH = 20
MAX_DETAILS_LENGTH = 150

NUM_USERS = 300
NUM_MESSAGES = 500
NUM_LISTINGS = 100

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
            email=fake.email(),
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password='$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe',
            phone=fake.phone_number()
        ))