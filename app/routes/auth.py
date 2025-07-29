from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.models import UserRegister, UserLogin, UserResponse, AuthResponse
from app.config import settings
from app.middleware.auth import verify_token
from typing import Dict, Any


router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (replace with database in production)
users: Dict[str, Dict[str, Any]] = {}

# Demo users configuration
DEMO_USERS = [
    {
        "email": "demo@example.com",
        "password": "demo",
        "name": "Demo User",
        "id": "demo1"
    },
    {
        "email": "demo@istqb.com",
        "password": "demo123",
        "name": "ISTQB Demo User",
        "id": "demo2"
    }
]

# Automatically create demo users if they don't exist
for demo_user in DEMO_USERS:
    if demo_user["email"] not in users:
        hashed_password = pwd_context.hash(demo_user["password"])
        users[demo_user["email"]] = {
            "id": demo_user["id"],
            "email": demo_user["email"],
            "password": hashed_password,
            "name": demo_user["name"],
            "createdAt": datetime.now().isoformat()
        }
        print(f"[OK] Created demo user: {demo_user['email']}")


def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Check if user already exists
        if user_data.email in users:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "User already exists",
                    "message": "A user with this email already exists"
                }
            )

        # Hash password
        hashed_password = pwd_context.hash(user_data.password)

        # Create user object
        user = {
            "id": str(int(datetime.now().timestamp())),
            "email": user_data.email,
            "name": user_data.name,
            "password": hashed_password,
            "createdAt": datetime.now().isoformat()
        }

        # Store user
        users[user_data.email] = user

        # Generate JWT token
        token = create_access_token({
            "userId": user["id"],
            "email": user["email"]
        })

        return AuthResponse(
            message="User registered successfully",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"]
            ),
            token=token
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Registration failed",
                "message": "An error occurred during registration"
            }
        )


@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLogin):
    """Authenticate user and return token"""
    try:
        # Find user
        user = users.get(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Check password
        if not pwd_context.verify(user_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Generate JWT token
        token = create_access_token({
            "userId": user["id"],
            "email": user["email"]
        })

        return AuthResponse(
            message="Login successful",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"]
            ),
            token=token
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Login failed",
                "message": "An error occurred during login"
            }
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: Dict[str, Any] = Depends(verify_token)):
    """Get current user info"""
    user = users.get(current_user["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"}
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        createdAt=user["createdAt"]
    )
