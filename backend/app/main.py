"""
FastAPI ACI Dashboard Application
Main application entry point with all routes and middleware
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.routers import auth_router, admin_router, tools_router, users_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Validation error"}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "message": "Invalid value provided"}
    )

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(tools_router)
app.include_router(users_router)

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Import here to avoid circular imports
        from app.db.session import get_db
        from sqlalchemy import text
        
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.VERSION
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected", 
                "error": str(e)
            }
        )

# Reset Password Models
class ResetPasswordRequest(BaseModel):
    username: str
    current_password: str
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str

# Reset Password Endpoint
@app.post("/api/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_user_password(request: ResetPasswordRequest):
    """Simple reset password endpoint"""
    try:
        from app.db.session import get_db
        from app.models.user import User
        from app.core.security import verify_password, hash_password
        import re
        
        db = next(get_db())
        
        # Find user
        user = db.query(User).filter(User.username == request.username.lower()).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify current password
        if not verify_password(request.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Validate new password strength
        if len(request.new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", request.new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", request.new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
        if not re.search(r"\d", request.new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", request.new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one special character")
        
        # Update password
        user.password_hash = hash_password(request.new_password)
        db.commit()
        db.close()
        
        return ResetPasswordResponse(message="Password reset successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)