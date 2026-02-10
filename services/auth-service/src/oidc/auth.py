"""OIDC authentication module."""
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from finops_common.context import get_context, set_context_values

from oidc.jwt_utils import JWTValidator


class OIDCAuth:
    """OIDC authentication handler."""

    def __init__(self, jwt_validator: JWTValidator):
        """Initialize OIDC auth.

        Args:
            jwt_validator: JWT validator instance
        """
        self.jwt_validator = jwt_validator

    async def get_current_user(
        self,
        authorization: Optional[str] = Header(None),
    ) -> dict:
        """Get current user from Bearer token.

        Args:
            authorization: Authorization header

        Returns:
            User information dictionary

        Raises:
            HTTPException: If token is missing or invalid
        """
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token from Bearer scheme
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        # Validate token
        payload = self.jwt_validator.validate_token(token)

        # Extract user information
        user_info = self.jwt_validator.extract_user_info(payload)

        # Set user context for request
        set_context_values(
            user_id=user_info["user_id"],
            org_id=user_info.get("org_id"),
            tenant_id=user_info.get("tenant_id"),
        )

        return user_info

    async def get_optional_user(
        self,
        authorization: Optional[str] = Header(None),
    ) -> Optional[dict]:
        """Get current user from Bearer token (optional).

        Args:
            authorization: Authorization header

        Returns:
            User information dictionary or None if no token
        """
        if not authorization:
            return None

        try:
            return await self.get_current_user(authorization)
        except HTTPException:
            return None


def get_oidc_auth() -> OIDCAuth:
    """Dependency to get OIDC auth instance.

    This should be overridden in main.py with actual configuration.
    """
    raise NotImplementedError("OIDC auth not configured")
