"""
Unified Exception Handling System
SpringBoot-style exception handling with standardized error codes
"""

from fastapi import HTTPException, status
from typing import Any, Optional


class AppException(HTTPException):
    """Base application exception with standardized error format"""

    def __init__(
        self,
        code: int,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details
            }
        )


class NotFoundException(AppException):
    """404 Not Found"""

    def __init__(self, message: str = "Resource not found", code: int = 40401, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ForbiddenException(AppException):
    """403 Forbidden"""

    def __init__(self, message: str = "Access denied", code: int = 40301, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class UnauthorizedException(AppException):
    """401 Unauthorized"""

    def __init__(self, message: str = "Authentication required", code: int = 40101, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class BadRequestException(AppException):
    """400 Bad Request"""

    def __init__(self, message: str = "Bad request", code: int = 40001, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class ConflictException(AppException):
    """409 Conflict"""

    def __init__(self, message: str = "Resource conflict", code: int = 40901, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_409_CONFLICT, details=details)


class ValidationException(AppException):
    """422 Validation Error"""

    def __init__(self, message: str = "Validation error", code: int = 42201, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class InternalServerException(AppException):
    """500 Internal Server Error"""

    def __init__(self, message: str = "Internal server error", code: int = 50001, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


# Domain-specific exceptions

class OrganizationNotFoundException(NotFoundException):
    def __init__(self, org_id: str):
        super().__init__(message=f"Organization not found: {org_id}", code=40401)


class ProjectNotFoundException(NotFoundException):
    def __init__(self, project_id: str):
        super().__init__(message=f"Project not found: {project_id}", code=40402)


class AgentNotFoundException(NotFoundException):
    def __init__(self, agent_id: str):
        super().__init__(message=f"Agent not found: {agent_id}", code=40403)


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__(message=f"User not found: {user_id}", code=40404)


class ProjectMemberNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(message="Project member not found", code=40405)


class InvalidProjectRoleException(ForbiddenException):
    def __init__(self, required_roles: list[str]):
        super().__init__(
            message=f"Admin or owner role required. Required roles: {', '.join(required_roles)}",
            code=40302
        )


class CannotRemoveOwnerException(ForbiddenException):
    def __init__(self):
        super().__init__(message="Cannot remove project owner", code=40303)


class UserAlreadyMemberException(ConflictException):
    def __init__(self):
        super().__init__(message="User is already a project member", code=40902)


class AgentAlreadyAssignedException(ConflictException):
    def __init__(self):
        super().__init__(message="Agent already assigned to this project", code=40903)


class AgentNotAssignedException(NotFoundException):
    def __init__(self):
        super().__init__(message="Agent not assigned to this project", code=40406)


# Auth exceptions
class EmailAlreadyRegisteredException(ConflictException):
    def __init__(self):
        super().__init__(message="Email already registered", code=40904)


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__(message="Invalid email or password", code=40102)


class InvalidRefreshTokenException(UnauthorizedException):
    def __init__(self):
        super().__init__(message="Invalid refresh token", code=40103)


class UserInactiveException(UnauthorizedException):
    def __init__(self):
        super().__init__(message="User is inactive", code=40104)


# Organization exceptions
class InvitationNotPendingException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invitation is not pending", code=40002)


class InvitationExpiredException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invitation has expired", code=40003)


class AlreadyMemberException(ConflictException):
    def __init__(self):
        super().__init__(message="Already a member", code=40905)


class OnlyOwnerCanRevokeException(ForbiddenException):
    def __init__(self):
        super().__init__(message="Only owner can revoke invitations", code=40304)


# Error code constants for documentation
class ErrorCodes:
    # 4xx Client Errors
    BAD_REQUEST = 40001
    UNAUTHORIZED = 40101
    FORBIDDEN_ACCESS = 40301
    INVALID_PROJECT_ROLE = 40302
    CANNOT_REMOVE_OWNER = 40303
    NOT_FOUND = 40401
    RESOURCE_NOT_FOUND = 40402
    PROJECT_NOT_FOUND = 40402
    AGENT_NOT_FOUND = 40403
    USER_NOT_FOUND = 40404
    PROJECT_MEMBER_NOT_FOUND = 40405
    AGENT_NOT_ASSIGNED = 40406
    CONFLICT = 40901
    USER_ALREADY_MEMBER = 40902
    AGENT_ALREADY_ASSIGNED = 40903
    VALIDATION_ERROR = 42201

    # 5xx Server Errors
    INTERNAL_ERROR = 50001
    DATABASE_ERROR = 50002
    EXTERNAL_SERVICE_ERROR = 50003