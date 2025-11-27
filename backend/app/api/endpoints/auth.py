from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.mongodb import get_database
from app.models.user import UserCreate, UserInDB, Token, TokenData
from jose import JWTError, jwt
from app.core.config import settings
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, EmailStr
import secrets
from app.core.mail import send_email

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception
    
    try:
        db = await get_database()
        user = await db.users.find_one({"email": token_data.email})
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        logger.error(f"Database error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        db = await get_database()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        user_data = user.model_dump(exclude={"password"})
        user_in_db = UserInDB(
            **user_data,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        # Insert into database
        await db.users.insert_one(user_in_db.model_dump())
        logger.info(f"Successfully registered user: {user.email}")
        
        # Create and return access token
        access_token = create_access_token(subject=user.email)
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        db = await get_database()
        user = await db.users.find_one({"email": form_data.username})
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Successful login for user: {form_data.username}")
        access_token = create_access_token(subject=user["email"])
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )

# Forgot Password Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    try:
        db = await get_database()
        user = await db.users.find_one({"email": request.email})
        if not user:
            # Don't reveal if user exists
            return {"message": "If the email exists, an OTP has been sent."}
        
        # Rate Limiting: Check if OTP was requested in the last minute
        if user.get("last_otp_request"):
            time_since_last = datetime.utcnow() - user["last_otp_request"]
            if time_since_last < timedelta(minutes=1):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Please wait 1 minute before requesting another OTP."
                )

        # Generate OTP
        otp = "".join([str(secrets.choice("0123456789")) for _ in range(6)])
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Save OTP and timestamp to DB
        await db.users.update_one(
            {"email": request.email},
            {"$set": {
                "otp": otp, 
                "otp_expiry": otp_expiry,
                "last_otp_request": datetime.utcnow()
            }}
        )
        
        # Send Email
        email_sent = await send_email(
            email=[request.email],
            subject="Med AI Password Reset OTP",
            body=f"Your OTP for password reset is: <b>{otp}</b>. It expires in 10 minutes."
        )
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send email. Please check server logs.")
        
        return {"message": "If the email exists, an OTP has been sent."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    try:
        db = await get_database()
        user = await db.users.find_one({"email": request.email})
        
        if not user or not user.get("otp") or not user.get("otp_expiry"):
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        if user["otp"] != request.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        if user["otp_expiry"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        return {"message": "OTP verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify OTP error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    try:
        db = await get_database()
        user = await db.users.find_one({"email": request.email})
        
        if not user or not user.get("otp") or not user.get("otp_expiry"):
            raise HTTPException(status_code=400, detail="Invalid request")
            
        if user["otp"] != request.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        if user["otp_expiry"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        # Hash new password
        hashed_password = get_password_hash(request.new_password)
        
        # Update password and clear OTP
        await db.users.update_one(
            {"email": request.email},
            {"$set": {"hashed_password": hashed_password, "otp": None, "otp_expiry": None}}
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")