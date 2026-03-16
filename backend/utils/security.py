from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if not token:
            logger.error("Token is empty or None")
            return None
        if not SECRET_KEY:
            logger.error("SECRET_KEY is not configured!")
            return None
        
        logger.info(f"Decoding token (first 20 chars): {token[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token decoded successfully: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        # Invalid token
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        # Unexpected error
        logger.error(f"Token decode error: {str(e)}")
        return None