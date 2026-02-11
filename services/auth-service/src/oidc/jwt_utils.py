"""JWT utilities for token validation and generation."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

logger = logging.getLogger(__name__)


class JWTValidator:
    """JWT token validator with Keycloak OIDC support."""

    def __init__(
        self,
        jwks_uri: str,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        algorithms: list[str] = None,
    ):
        """Initialize JWT validator.

        Args:
            jwks_uri: JWKS URI for fetching public keys
            issuer: Expected token issuer
            audience: Expected token audience
            algorithms: Allowed signing algorithms
        """
        self.jwks_uri = jwks_uri
        self.issuer = issuer
        self.audience = audience
        self.algorithms = algorithms or ["RS256", "HS256"]
        
        # Initialize JWKS client for key fetching
        self.jwks_client = PyJWKClient(jwks_uri, cache_keys=True)
        logger.info(f"JWT validator initialized with JWKS URI: {jwks_uri}")

    def validate_token(self, token: str) -> Dict:
        """Validate JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload as dictionary

        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and validate token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.algorithms,
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": bool(self.audience),
                    "verify_iss": bool(self.issuer),
                },
            )
            
            logger.debug(f"Token validated successfully for user: {payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def extract_user_info(self, payload: Dict) -> Dict:
        """Extract user information from token payload.

        Args:
            payload: JWT token payload

        Returns:
            User information dictionary
        """
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("preferred_username") or payload.get("username"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "given_name": payload.get("given_name"),
            "family_name": payload.get("family_name"),
            "roles": payload.get("realm_access", {}).get("roles", []),
            "groups": payload.get("groups", []),
            "org_id": payload.get("org_id"),  # Custom claim
            "tenant_id": payload.get("tenant_id"),  # Custom claim
        }


class JWTGenerator:
    """JWT token generator for internal use."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7,
    ):
        """Initialize JWT generator.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: Signing algorithm
            issuer: Token issuer
            audience: Token audience
            access_token_expire_minutes: Access token expiry in minutes
            refresh_token_expire_days: Refresh token expiry in days
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        subject: str,
        claims: Optional[Dict] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create access token.

        Args:
            subject: Token subject (user ID)
            claims: Additional claims to include
            expires_delta: Custom expiration time

        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        if self.issuer:
            payload["iss"] = self.issuer
        if self.audience:
            payload["aud"] = self.audience
        if claims:
            payload.update(claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def create_refresh_token(self, subject: str) -> str:
        """Create refresh token.

        Args:
            subject: Token subject (user ID)

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        if self.issuer:
            payload["iss"] = self.issuer

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
