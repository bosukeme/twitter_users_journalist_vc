from decouple import config as env_config

# MONGO_URL = env_config("MONGO_URL")
CONSUMER_KEY = env_config("CONSUMER_KEY")
CONSUMER_SECRET = env_config("CONSUMER_SECRET")
ACCESS_TOKEN = env_config("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = env_config("ACCESS_TOKEN_SECRET")

MONGODB_USERNAME = env_config('MONGODB_USERNAME')
MONGODB_PASSWORD = env_config('MONGODB_PASSWORD')
