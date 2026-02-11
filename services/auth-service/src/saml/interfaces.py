"""SAML interfaces and types - Scaffolding only.

This module defines interfaces for SAML authentication integration.
Actual implementation will be added in future iterations.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SAMLUser:
    """SAML user information."""

    name_id: str
    session_index: Optional[str] = None
    attributes: dict = None

    def __post_init__(self):
        """Initialize attributes dictionary."""
        if self.attributes is None:
            self.attributes = {}


@dataclass
class SAMLRequest:
    """SAML authentication request."""

    request_id: str
    issuer: str
    destination: str
    assertion_consumer_service_url: str
    name_id_format: str


@dataclass
class SAMLResponse:
    """SAML authentication response."""

    response_id: str
    issuer: str
    status_code: str
    assertion: Optional[str] = None
    name_id: Optional[str] = None
    attributes: dict = None

    def __post_init__(self):
        """Initialize attributes dictionary."""
        if self.attributes is None:
            self.attributes = {}


class ISAMLIdentityProvider(ABC):
    """Interface for SAML Identity Provider operations."""

    @abstractmethod
    async def initiate_sso(
        self,
        relay_state: Optional[str] = None,
    ) -> str:
        """Initiate SSO flow with IdP.

        Args:
            relay_state: Optional relay state to maintain across SSO flow

        Returns:
            Redirect URL to IdP
        """
        pass

    @abstractmethod
    async def process_response(
        self,
        saml_response: str,
        relay_state: Optional[str] = None,
    ) -> SAMLUser:
        """Process SAML response from IdP.

        Args:
            saml_response: Base64 encoded SAML response
            relay_state: Optional relay state from request

        Returns:
            SAML user information

        Raises:
            SAMLError: If response validation fails
        """
        pass

    @abstractmethod
    async def logout(
        self,
        name_id: str,
        session_index: Optional[str] = None,
    ) -> str:
        """Initiate single logout.

        Args:
            name_id: User name ID
            session_index: Session index from authentication

        Returns:
            Redirect URL to IdP for logout
        """
        pass


class ISAMLServiceProvider(ABC):
    """Interface for SAML Service Provider operations."""

    @abstractmethod
    async def get_metadata(self) -> str:
        """Get SP metadata XML.

        Returns:
            SAML metadata XML string
        """
        pass

    @abstractmethod
    async def validate_assertion(
        self,
        assertion: str,
    ) -> bool:
        """Validate SAML assertion.

        Args:
            assertion: SAML assertion XML

        Returns:
            True if assertion is valid

        Raises:
            SAMLError: If assertion validation fails
        """
        pass


class ISAMLMetadataProvider(ABC):
    """Interface for SAML metadata management."""

    @abstractmethod
    async def get_sp_metadata(self) -> str:
        """Get Service Provider metadata.

        Returns:
            SP metadata XML
        """
        pass

    @abstractmethod
    async def get_idp_metadata(self, idp_entity_id: str) -> str:
        """Get Identity Provider metadata.

        Args:
            idp_entity_id: IdP entity ID

        Returns:
            IdP metadata XML
        """
        pass

    @abstractmethod
    async def update_idp_metadata(
        self,
        idp_entity_id: str,
        metadata_xml: str,
    ) -> None:
        """Update IdP metadata.

        Args:
            idp_entity_id: IdP entity ID
            metadata_xml: New metadata XML
        """
        pass


class SAMLError(Exception):
    """SAML-specific error."""

    pass


class SAMLValidationError(SAMLError):
    """SAML validation error."""

    pass


class SAMLConfigurationError(SAMLError):
    """SAML configuration error."""

    pass
