"""Tests for auth service configuration."""
import os
from unittest.mock import patch

import pytest

from finops_config import AuthServiceConfig


def test_auth_config_defaults():
    """Test default configuration values."""
    config = AuthServiceConfig()
    
    assert config.service_name == "auth-service"
    assert config.port == 8001
    assert config.keycloak.server_url == "http://keycloak:8081"
    assert config.keycloak.realm == "finops"
    assert config.jwt.algorithm == "HS256"
    assert config.jwt.access_token_expire_minutes == 60


def test_auth_config_from_env():
    """Test loading configuration from environment variables."""
    env_vars = {
        "AUTH_SERVICE_NAME": "test-auth-service",
        "AUTH_PORT": "9001",
        "AUTH_KEYCLOAK__SERVER_URL": "http://keycloak-test:8080",
        "AUTH_KEYCLOAK__REALM": "test-realm",
        "AUTH_KEYCLOAK__CLIENT_ID": "test-client",
        "AUTH_JWT__SECRET_KEY": "test-secret",
        "AUTH_JWT__ALGORITHM": "RS256",
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        config = AuthServiceConfig()
        
        assert config.service_name == "test-auth-service"
        assert config.port == 9001
        assert config.keycloak.server_url == "http://keycloak-test:8080"
        assert config.keycloak.realm == "test-realm"
        assert config.keycloak.client_id == "test-client"
        assert config.jwt.secret_key == "test-secret"
        assert config.jwt.algorithm == "RS256"


def test_keycloak_urls():
    """Test Keycloak URL generation."""
    config = AuthServiceConfig()
    
    assert config.keycloak.well_known_url == "http://keycloak:8081/realms/finops/.well-known/openid-configuration"
    assert config.keycloak.jwks_uri == "http://keycloak:8081/realms/finops/protocol/openid-connect/certs"
    assert config.keycloak.token_endpoint == "http://keycloak:8081/realms/finops/protocol/openid-connect/token"
    assert config.keycloak.userinfo_endpoint == "http://keycloak:8081/realms/finops/protocol/openid-connect/userinfo"
    assert config.keycloak.logout_endpoint == "http://keycloak:8081/realms/finops/protocol/openid-connect/logout"


def test_kafka_topics():
    """Test Kafka topics configuration."""
    config = AuthServiceConfig()
    
    assert config.kafka_topics.user_events == "user-events"
    assert config.kafka_topics.login_events == "login-events"
    assert config.kafka_topics.permission_changes == "permission-changes"
    assert config.kafka_topics.session_events == "session-events"
    
    # Test full topic names with prefix
    assert config.kafka_topics.get_full_topic_name("user-events") == "finops.user-events"


def test_kafka_producer_config():
    """Test Kafka producer configuration."""
    config = AuthServiceConfig()
    
    producer_config = config.kafka.get_producer_config()
    
    assert producer_config["bootstrap_servers"] == ["kafka:9092"]
    assert producer_config["acks"] == "all"
    assert producer_config["retries"] == 3


def test_kafka_consumer_config():
    """Test Kafka consumer configuration."""
    config = AuthServiceConfig()
    
    consumer_config = config.kafka.get_consumer_config("test-group")
    
    assert consumer_config["bootstrap_servers"] == ["kafka:9092"]
    assert consumer_config["group_id"] == "test-group"
    assert consumer_config["auto_offset_reset"] == "earliest"


def test_saml_config():
    """Test SAML configuration."""
    config = AuthServiceConfig()
    
    assert config.saml.enabled is False
    assert config.saml.name_id_format == "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    
    # Test with SAML enabled
    env_vars = {
        "AUTH_SAML__ENABLED": "true",
        "AUTH_SAML__SP_ENTITY_ID": "https://finops.example.com",
        "AUTH_SAML__IDP_ENTITY_ID": "https://idp.example.com",
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        config = AuthServiceConfig()
        assert config.saml.enabled is True
        assert config.saml.sp_entity_id == "https://finops.example.com"
        assert config.saml.idp_entity_id == "https://idp.example.com"


def test_scim_config():
    """Test SCIM configuration."""
    config = AuthServiceConfig()
    
    assert config.scim.enabled is False
    assert config.scim.user_schema_version == "urn:ietf:params:scim:schemas:core:2.0:User"


def test_session_config():
    """Test session configuration."""
    config = AuthServiceConfig()
    
    assert config.session_cookie_name == "finops_session"
    assert config.session_cookie_httponly is True
    assert config.session_cookie_samesite == "lax"
    assert config.session_max_age == 86400


def test_rate_limiting_config():
    """Test rate limiting configuration."""
    config = AuthServiceConfig()
    
    assert config.rate_limit_enabled is True
    assert config.rate_limit_per_minute == 60
