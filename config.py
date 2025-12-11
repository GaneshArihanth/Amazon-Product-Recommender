import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
