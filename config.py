import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App Configuration
DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
