#!/usr/bin/env python3
"""
VoidLink Error Handling Module - Provides centralized error handling and logging
"""

import logging
import os
import sys
import traceback
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
LOG_FILE = f"logs/voidlink_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger('voidlink')


class VoidLinkError(Exception):
    """Base exception for VoidLink errors"""

    def __init__(self, message: str, error_code: int = 500,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

        # Log the error
        logger.error(f"Error {error_code}: {message}")
        if details:
            logger.error(f"Details: {details}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for client response"""
        return {
            "type": "error",
            "code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(VoidLinkError):
    """Authentication related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)


class AuthorizationError(VoidLinkError):
    """Authorization related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)


class FileTransferError(VoidLinkError):
    """File transfer related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class FileSecurityError(VoidLinkError):
    """File security related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class RoomError(VoidLinkError):
    """Chat room related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


class ConfigurationError(VoidLinkError):
    """Configuration related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)


class NetworkError(VoidLinkError):
    """Network related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)


def log_info(message: str) -> None:
    """Log an informational message"""
    logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message"""
    logger.warning(message)


def log_error(message: str, exc_info: bool = False) -> None:
    """Log an error message"""
    if exc_info:
        logger.error(message, exc_info=True)
    else:
        logger.error(message)


def log_exception(e: Exception, context: str = "") -> None:
    """Log an exception with context"""
    if context:
        logger.error(f"Exception in {context}: {str(e)}")
    else:
        logger.error(f"Exception: {str(e)}")
    logger.error(traceback.format_exc())


def handle_client_error(error: VoidLinkError) -> Dict[str, Any]:
    """Format an error for client response"""
    return error.to_dict()


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger for a specific module"""
    module_logger = logging.getLogger(f'voidlink.{name}')
    module_logger.setLevel(level)
    return module_logger
