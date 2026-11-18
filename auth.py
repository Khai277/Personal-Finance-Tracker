import os
from dotenv import load_dotenv
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone


load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

def create_access_token(username):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)

    token = jwt.encode(
        {
            "sub": username,
            "exp": expiration
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def decode_access_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])