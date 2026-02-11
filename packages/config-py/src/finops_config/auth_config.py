"""Authentication service configuration."""
from typing import Optional

from pydantic import Field, HttpUrl

from finops_config.base import BaseServiceConfig
from finops_config.kafka import AuthKafkaTopicsConfig, KafkaConfig


class KeycloakConfig(BaseModel):
    """Keycloak/OIDC configuration."""

    server_url: str = Field(
        default="http://keycloak:8081",
        description="Keycloak server URL",
    )
    realm: str = Field(
        default="finops",
        description="Keycloak realm name",
    )
    client_id: str = Field(
        default="finops-auth",
        description="OAuth2/OIDC client ID",
    )
    client_secret: Optional[str] = Field(
        default=None,
        description="OAuth2/OIDC client secret",
    )
    admin_username: Optional[str] = Field(
        default=None,
        description="Keycloak admin username",
    )
    admin_password: Optional[str] = Field(
        default=None,
        description="Keycloak admin password",
    )
    
    # Token validation
    token_verify_signature: bool = Field(
        default=True,
        description="Verify JWT signature",
    )
    token_verify_audience: bool = Field(
        default=True,
        description="Verify JWT audience",
    )
    token_verify_exp: bool = Field(
        default=True,
        description="Verify JWT expiration",
    )
    
    # Caching
    cache_jwks: bool = Field(
        default=True,
        description="Cache JWKS keys",
    )
    cache_jwks_ttl: int = Field(
        default=3600,
        description="JWKS cache TTL in seconds",
    )

    @property
    def well_known_url(self) -> str:
        """Get OpenID Connect discovery URL."""
        return f"{self.server_url}/realms/{self.realm}/.well-known/openid-configuration"

    @property
    def jwks_uri(self) -> str:
        """Get JWKS URI."""
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/certs"

    @property
    def token_endpoint(self) -> str:
        """Get token endpoint."""
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"

    @property
    def userinfo_endpoint(self) -> str:
        """Get userinfo endpoint."""
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/userinfo"

    @property
    def logout_endpoint(self) -> str:
        """Get logout endpoint."""
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/logout"


class JWTConfig(BaseModel):
    """JWT configuration."""

    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT secret key for signing (if not using OIDC)",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        description="Access token expiry in minutes",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiry in days",
    )
    issuer: Optional[str] = Field(
        default="finops-auth-service",
        description="JWT issuer",
    )
    audience: Optional[str] = Field(
        default="finops-api",
        description="JWT audience",
    )


class SAMLConfig(BaseModel):
    """SAML configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable SAML authentication",
    )
    
    # Service Provider (SP) configuration
    sp_entity_id: Optional[str] = Field(
        default=None,
        description="Service Provider entity ID",
    )
    sp_acs_url: Optional[str] = Field(
        default=None,
        description="Assertion Consumer Service URL",
    )
    sp_x509_cert: Optional[str] = Field(
        default=None,
        description="SP X.509 certificate (PEM format)",
    )
    sp_private_key: Optional[str] = Field(
        default=None,
        description="SP private key (PEM format)",
    )
    
    # Identity Provider (IdP) configuration
    idp_entity_id: Optional[str] = Field(
        default=None,
        description="Identity Provider entity ID",
    )
    idp_sso_url: Optional[str] = Field(
        default=None,
        description="IdP Single Sign-On URL",
    )
    idp_x509_cert: Optional[str] = Field(
        default=None,
        description="IdP X.509 certificate (PEM format)",
    )
    
    # SAML settings
    name_id_format: str = Field(
        default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        description="NameID format",
    )
    authn_context: list[str] = Field(
        default_factory=lambda: [
            "urn:oasis:names:tc:SAML:2.0:ac:classes:Password",
        ],
        description="Authentication context classes",
    )


class SCIMConfig(BaseModel):
    """SCIM (System for Cross-domain Identity Management) configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable SCIM provisioning",
    )
    api_token: Optional[str] = Field(
        default=None,
        description="SCIM API token for authentication",
    )
    user_schema_version: str = Field(
        default="urn:ietf:params:scim:schemas:core:2.0:User",
        description="SCIM user schema version",
    )
    group_schema_version: str = Field(
        default="urn:ietf:params:scim:schemas:core:2.0:Group",
        description="SCIM group schema version",
    )


class AuthServiceConfig(BaseServiceConfig):
    """Authentication service configuration."""

    # Service identity override
    service_name: str = Field(default="auth-service", description="Service name")
    port: int = Field(default=8001, description="Server port")

    # Database override (required for auth service)
    database_url: str = Field(
        default="postgresql://finops:finops_dev_password@postgres:5432/finops",
        description="Database connection URL",
    )

    # Keycloak/OIDC
    keycloak: KeycloakConfig = Field(
        default_factory=KeycloakConfig,
        description="Keycloak configuration",
    )

    # JWT (for internal token generation)
    jwt: JWTConfig = Field(
        default_factory=JWTConfig,
        description="JWT configuration",
    )

    # SAML
    saml: SAMLConfig = Field(
        default_factory=SAMLConfig,
        description="SAML configuration",
    )

    # SCIM
    scim: SCIMConfig = Field(
        default_factory=SCIMConfig,
        description="SCIM configuration",
    )

    # Kafka
    kafka: KafkaConfig = Field(
        default_factory=KafkaConfig,
        description="Kafka configuration",
    )
    kafka_topics: AuthKafkaTopicsConfig = Field(
        default_factory=AuthKafkaTopicsConfig,
        description="Auth service Kafka topics",
    )

    # Session management
    session_cookie_name: str = Field(
        default="finops_session",
        description="Session cookie name",
    )
    session_cookie_secure: bool = Field(
        default=False,
        description="Use secure cookies (HTTPS only)",
    )
    session_cookie_httponly: bool = Field(
        default=True,
        description="HttpOnly cookie flag",
    )
    session_cookie_samesite: str = Field(
        default="lax",
        description="SameSite cookie attribute",
    )
    session_max_age: int = Field(
        default=86400,
        description="Session max age in seconds (24 hours)",
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    rate_limit_per_minute: int = Field(
        default=60,
        description="Max requests per minute per IP",
    )

    class Config:
        """Pydantic configuration."""
        env_prefix = "AUTH_"
        env_nested_delimiter = "__"


# Import statement for BaseModel
from pydantic import BaseModel
