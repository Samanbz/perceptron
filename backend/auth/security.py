"""
Password hashing and JWT token utilities
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    print(f"🔍 Verifying password - length: {len(plain_password)} chars")
    # Simply truncate to 72 characters (bcrypt limit)
    if len(plain_password) > 72:
        print(f"⚠️ Password too long, truncating from {len(plain_password)} to 72")
        plain_password = plain_password[:72]
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"✅ Password verification: {result}")
        return result
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        raise

def get_password_hash(password: str) -> str:
    """Hash a password"""
    print(f"🔐 Hashing password - length: {len(password)} chars")
    # Simply truncate to 72 characters (bcrypt limit)
    if len(password) > 72:
        print(f"⚠️ Password too long, truncating from {len(password)} to 72")
        password = password[:72]
    try:
        result = pwd_context.hash(password)
        print(f"✅ Password hashed successfully")
        return result
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    """Decode a JWT access token and return the email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None
