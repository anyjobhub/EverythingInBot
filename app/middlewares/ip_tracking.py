"""
IP Tracking Middleware for FastAPI
Captures client IP address and User-Agent from request headers
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class IPTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and store IP address and User-Agent
    from incoming requests for logging purposes
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request and extract tracking information
        """
        try:
            # Get real IP address (check X-Forwarded-For first, then X-Real-IP, then direct)
            ip_address = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or request.headers.get("X-Real-IP", "").strip()
                or request.client.host if request.client else "unknown"
            )
            
            # Get User-Agent
            user_agent = request.headers.get("User-Agent", "unknown")
            
            # Store in request state for handlers to access
            request.state.ip_address = ip_address
            request.state.user_agent = user_agent
            
        except Exception as e:
            logger.error(f"Error in IP tracking middleware: {str(e)}")
            request.state.ip_address = "unknown"
            request.state.user_agent = "unknown"
        
        # Continue processing request
        response = await call_next(request)
        return response
