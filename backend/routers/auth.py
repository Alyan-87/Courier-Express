from fastapi import APIRouter, Depends, HTTPException
from schemas.pydantic_schemas import UserCreate, LoginRequest, UserOut, Token
from models.sql_models import user_document
from utils.security import get_password_hash, create_access_token, verify_password
from config.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db=Depends(get_db)):
    try:
        # Log sanitized incoming registration attempt (do NOT log raw password)
        try:
            pw_len = len(user.password.encode('utf-8')) if user.password else 0
        except Exception:
            pw_len = -1
        logger.info(f"Register attempt: email={user.email}, name={user.name}, role={user.role}, phone_present={bool(user.phone)}, pw_bytes={pw_len}")
        
        # Validate inputs
        if not user.name or not user.name.strip():
            raise HTTPException(400, "Name is required")
        if not user.email or not user.email.strip():
            raise HTTPException(400, "Email is required")
        if not user.password or len(user.password) < 6:
            raise HTTPException(400, "Password must be at least 6 characters")
        if user.role not in ["customer", "staff", "rider"]:
            raise HTTPException(400, "Invalid role. Must be customer, staff, or rider")
        
        # Check if email already exists
        existing_user = db["users"].find_one({"email": user.email})
        if existing_user:
            raise HTTPException(400, "Email already registered")

        # Hash password
        hashed = get_password_hash(user.password)

        new_user = user_document(user.name, user.email, user.phone, hashed, user.role)
        result = db["users"].insert_one(new_user)
        return {
            "user_id": str(result.inserted_id),
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"],
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log full exception with traceback for debugging (server-side only)
        logger.exception("Registration error")
        raise HTTPException(500, "Registration failed — server error")

@router.post("/login", response_model=Token)
def login(user: LoginRequest, db=Depends(get_db)):
    try:
        # Validate inputs
        if not user.email or not user.email.strip():
            raise HTTPException(400, "Email is required")
        if not user.password:
            raise HTTPException(400, "Password is required")
        
        db_user = db["users"].find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(401, "Invalid email or password")

        token = create_access_token({"sub": db_user["email"], "role": db_user["role"]})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(500, "Login failed")