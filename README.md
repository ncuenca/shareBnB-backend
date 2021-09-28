# ShareBnB

ShareBnB is a fullstack Airbnb clone where hosts can list their backyard or pool spaces for rent by other users. ShareBnB utilizes a React frontend, a Flask backend, and AWS S3 for photo uploads. For ease of deployment, the backend repository has been separated and can be found [here](https://github.com/mykeychain/shareBnB-frontend).

ShareBnB allows users to sign-up or login. Authentication is implemented with Bcrypt and persists with JSON Web Tokens. Once logged in, users have access to the following features: 

- view all current listings
- search for listings by name
- add a listing and upload their own photos
- send and receive private messages with other users

You can view the deployed version of ShareBnB [here](https://mikechang-sharebnb.surge.sh/).

The fake users, user information, and listings are created with Faker and are not real people nor addresses. 

<br>

## Setup Instructions

1. Navigate into ShareBnB backend directory `cd shareBnB-backend`
2. Create virtual environment `python -m venv venv`
3. Activate the virtual environment `source venv/bin/activate`
4. Install dependencies `pip install -r requirements.txt`
5. Create database `createdb sharebnb`
6. Seed database `python seed.py`
7. Run server on port 5000 `flask run --port=5000`
8. Clone and install the frontend repository [here](https://github.com/mykeychain/shareBnB-frontend). 

## Authors 

ShareBnB is authored by [Mike Chang](https://github.com/mykeychain) and [Nate Cuenca](https://github.com/ncuenca).

## Technologies Used
- [React](https://reactjs.org/) - Javascript frontend framework
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Python backend framework
- [PostgreSQL](https://www.postgresql.org/) - Relational database system
- [AWS S3](https://aws.amazon.com/s3/) - Cloud storage system