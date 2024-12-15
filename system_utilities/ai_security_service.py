# Main FastAPI backend service for AI security system

# Import required libraries and modules
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
from datetime import datetime
import jwt
import bcrypt
from typing import Optional
import os
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI(title="AI Security Backend Service")

# Set up database connection using environment variables or defaults
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoload=True, bind=engine)
Base = declarative_base()

# Configure Redis cache connection
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    decode_responses=True
)

# JWT configuration settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

# Define User model for database
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

# Middleware to verify JWT token and get current user
def get_current_user(token: str = Depends()):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Decorator for caching responses in Redis
def cache_response(expire_time=300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache for existing result
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result if not found
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, str(result))
            return result
        return wrapper
    return decorator

# Endpoint to create new user
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verify username is not taken
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user record
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    db_user = User(
        username=user.username,
        password_hash=hashed_password.decode()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Endpoint to get user details
@app.get("/api/users/{user_id}", response_model=UserResponse)
@cache_response(expire_time=300)
async def get_user(
    user_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Login endpoint to authenticate users
@app.post("/api/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(
        password.encode(),
        user.password_hash.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate and return JWT token
    token = jwt.encode(
        {"sub": user.username, "exp": datetime.utcnow()},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": "connected" if engine else "disconnected",
        "cache": "connected" if redis_client.ping() else "disconnected"
    }

# Main execution block
if __name__ == "__main__":
    # Initialize database schema
    Base.metadata.create_all(bind=engine)
    
    # Start uvicorn server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)