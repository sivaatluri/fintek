"""Authentication service for fintek platform."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from pydantic import BaseModel

from .health import router as health_router

app = FastAPI(
    title="Fintek Auth Service",
    description="Authentication and authorization service",
    version="0.1.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    """User login request."""
    email: str
    password: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-auth",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint (placeholder).
    
    In production, this would:
    - Validate credentials against database
    - Generate JWT token
    - Return token
    """
    # Placeholder implementation
    return {
        "access_token": "placeholder_token",
        "token_type": "bearer"
    }


@app.post("/auth/login", response_model=Token)
async def api_login(user_login: UserLogin):
    """API login endpoint (placeholder)."""
    return {
        "access_token": "placeholder_token",
        "token_type": "bearer"
    }


@app.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint (placeholder)."""
    return {"message": "Logged out successfully"}


@app.get("/auth/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user info (placeholder)."""
    return {
        "id": "user-123",
        "email": "user@example.com",
        "tenant_id": "tenant-123",
        "roles": ["tenant_user"],
    }


@app.post("/auth/verify")
async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verify token validity (placeholder)."""
    return {
        "valid": True,
        "user_id": "user-123",
        "tenant_id": "tenant-123",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
