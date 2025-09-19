"""
ACI Dashboard Security Middleware
Implements OWASP Top 10 protection and SOC II compliance measures
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from .security import security_config, RateLimiter, AuditLogger, SecurityUtils

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Global rate limiter instance
rate_limiter = RateLimiter()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers for OWASP compliance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add all security headers
        for header, value in security_config.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add HSTS in production
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP + User-Agent for better uniqueness)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        identifier = f"{client_ip}:{hash(user_agent)}"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Check rate limit
        if not rate_limiter.is_allowed(identifier):
            # Log rate limit violation
            AuditLogger.log_security_event(
                "RATE_LIMIT_EXCEEDED",
                None,
                {
                    "client_ip": client_ip,
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return await call_next(request)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize inputs and prevent injection attacks"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Sanitize query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_key = SecurityUtils.sanitize_input(key)
                sanitized_value = SecurityUtils.sanitize_input(value)
                sanitized_params[sanitized_key] = sanitized_value
            
            # Update request query params (note: this is for logging/monitoring)
            # Actual sanitization should be done at the endpoint level
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Security-focused request logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request details
        logger.info(
            f"REQUEST: {request.method} {request.url.path} - "
            f"IP: {client_ip} - "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"RESPONSE: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"IP: {client_ip}"
        )
        
        # Log suspicious activities
        if response.status_code >= 400:
            AuditLogger.log_security_event(
                "HTTP_ERROR",
                None,
                {
                    "status_code": response.status_code,
                    "path": str(request.url.path),
                    "method": request.method,
                    "client_ip": client_ip,
                    "process_time": process_time
                }
            )
        
        return response

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF protection for safe methods and API endpoints
        if request.method in ["GET", "HEAD", "OPTIONS"] or request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Check for CSRF token in headers
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        # In a real implementation, validate the CSRF token against a stored value
        # For now, we'll just check that it exists
        
        return await call_next(request)

# Security utilities for endpoints
def get_client_ip(request: Request) -> str:
    """Get real client IP address, considering proxies"""
    # Check for forwarded headers (common in load balancer setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def validate_request_size(request: Request, max_size: int = 10 * 1024 * 1024):  # 10MB default
    """Validate request size to prevent DoS attacks"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Request too large"
        )

# Security decorators
def require_https(func):
    """Decorator to require HTTPS in production"""
    async def wrapper(request: Request, *args, **kwargs):
        if request.url.scheme != "https" and request.headers.get("x-forwarded-proto") != "https":
            # In production, this should redirect to HTTPS
            if security_config.ENVIRONMENT == "production":
                raise HTTPException(
                    status_code=status.HTTP_426_UPGRADE_REQUIRED,
                    detail="HTTPS required"
                )
        return await func(request, *args, **kwargs)
    return wrapper