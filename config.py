import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///autosalon.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 МБ
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    INQUIRY_API_URL = os.getenv("INQUIRY_API_URL", "http://inquiries:8080")
    INQUIRY_API_KEY = os.getenv("INQUIRY_API_KEY", "super-secret-inquiries")
