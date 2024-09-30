from os import getenv
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI")
API_TOKEN = getenv("API_TOKEN")
