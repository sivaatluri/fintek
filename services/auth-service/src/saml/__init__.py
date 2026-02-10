"""SAML module - Scaffolding for SAML 2.0 authentication.

This module provides interfaces and basic structure for SAML authentication.
Full implementation will be added in future iterations based on requirements.

Key Components:
- ISAMLIdentityProvider: Interface for IdP operations
- ISAMLServiceProvider: Interface for SP operations
- ISAMLMetadataProvider: Interface for metadata management
- SAMLUser, SAMLRequest, SAMLResponse: Data classes

Integration Points:
1. Configure SAML in finops_config.SAMLConfig
2. Implement interfaces using python3-saml or similar library
3. Add endpoints in main.py for ACS, metadata, SLO
4. Store IdP configurations in database

Example Configuration:
```python
from finops_config import AuthServiceConfig

config = AuthServiceConfig()
config.saml.enabled = True
config.saml.sp_entity_id = "https://finops.example.com"
config.saml.idp_entity_id = "https://idp.example.com"
```

TODO:
- [ ] Implement ISAMLIdentityProvider
- [ ] Implement ISAMLServiceProvider  
- [ ] Add XML signature validation
- [ ] Add assertion encryption support
- [ ] Add metadata caching
- [ ] Add multi-IdP support
- [ ] Add SAML attribute mapping
- [ ] Add comprehensive tests
"""

from saml.interfaces import (
    ISAMLIdentityProvider,
    ISAMLMetadataProvider,
    ISAMLServiceProvider,
    SAMLConfigurationError,
    SAMLError,
    SAMLRequest,
    SAMLResponse,
    SAMLUser,
    SAMLValidationError,
)

__all__ = [
    "ISAMLIdentityProvider",
    "ISAMLServiceProvider",
    "ISAMLMetadataProvider",
    "SAMLUser",
    "SAMLRequest",
    "SAMLResponse",
    "SAMLError",
    "SAMLValidationError",
    "SAMLConfigurationError",
]
