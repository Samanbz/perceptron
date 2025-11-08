"""
Simple authentication routes - clean and minimal
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta

from .models import UserSignup, UserLogin, UserResponse, Token
from .security_v2 import create_access_token, verify_password, decode_token, ACCESS_TOKEN_EXPIRE_HOURS
from .repository_v2 import user_repository

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=Token)
async def signup(user: UserSignup):
    """Register new user"""
    try:
        # Create user
        db_user = user_repository.create_user(
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        
        # Create token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(db_user.id)},
            expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(db_user.id),
                "email": db_user.email,
                "full_name": db_user.full_name
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user"""
    # Get user
    db_user = user_repository.get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    user_repository.update_last_login(user.email)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(db_user.id)},
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "full_name": db_user.full_name
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db_user = user_repository.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": str(db_user.id),
        "email": db_user.email,
        "full_name": db_user.full_name
    }
