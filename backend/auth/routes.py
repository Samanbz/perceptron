"""
Authentication routes for user signup, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from .models import UserCreate, UserLogin, User, Token
from .repository import user_repository
from .security import verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception
    
    user = await user_repository.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        last_login=user.last_login,
        is_active=user.is_active
    )

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """
    Create a new user account
    
    - **email**: Valid email address
    - **name**: Full name of the user
    - **password**: Strong password (min 8 characters recommended)
    """
    try:
        print(f"🔵 Signup request received for: {user.email}")
        
        # Check if user already exists
        existing_user = await user_repository.get_user_by_email(user.email)
        if existing_user:
            print(f"❌ User already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        print(f"✅ Email is available, creating user...")
        
        # Create new user
        created_user = await user_repository.create_user(user)
        if not created_user:
            print(f"❌ Failed to create user in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        print(f"✅ User created successfully: {created_user.email}")
        
        return User(
            id=created_user.id,
            email=created_user.email,
            name=created_user.name,
            created_at=created_user.created_at,
            last_login=created_user.last_login,
            is_active=created_user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Unexpected error in signup: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password to get access token
    
    - **username**: Email address (OAuth2 standard uses 'username' field)
    - **password**: User password
    """
    # Get user by email
    user = await user_repository.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await user_repository.update_last_login(user.email)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin):
    """
    Login with JSON body (alternative to form data)
    
    - **email**: User email address
    - **password**: User password
    """
    # Get user by email
    user = await user_repository.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await user_repository.update_last_login(user.email)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    return current_user

@router.get("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    
    Returns user info if token is valid
    """
    return {
        "valid": True,
        "user": current_user
    }
