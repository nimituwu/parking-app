from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import os

# Argon2 is the absolute gold standard for password hashing, resistant to GPU cracking
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# In a real bank, this is injected via highly secure cloud vaults. We use an environment variable.
SECRET_KEY = os.getenv("SECRET_KEY", "extremely_secure_long_random_string_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
