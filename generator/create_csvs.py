from faker import Faker

USERS_CSV_HEADERS = ['email', 'username', 'password', 'phone', 'first_name', 'last_name', 'is_admin']
MESSAGES_CSV_HEADERS = ['text', 'to_user', 'from_user']
LISTINGS_CSV_HEADERS = ['photos', 'address', 'title', 'details', 'host', 'price']

MAX_MESSAGE_LENGTH = 150
MAX_TITLE_LENGTH = 20
MAX_DETAILS_LENGTH = 150

NUM_USERS = 300
NUM_MESSAGES = 500
NUM_LISTINGS = 100

fake = Faker()