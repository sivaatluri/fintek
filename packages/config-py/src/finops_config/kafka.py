"""Kafka configuration."""
from typing import Dict, Optional

from pydantic import BaseModel, Field


class KafkaTopicsConfig(BaseModel):
    """Kafka topics configuration."""

    # Base topic configuration
    prefix: str = Field(default="finops", description="Topic prefix")
    
    # Common topics (all services may use these)
    audit_events: str = Field(default="audit-events", description="Audit events topic")
    dlq: str = Field(default="dlq", description="Dead letter queue topic")
    
    def get_full_topic_name(self, topic: str) -> str:
        """Get full topic name with prefix."""
        return f"{self.prefix}.{topic}"


class AuthKafkaTopicsConfig(KafkaTopicsConfig):
    """Auth service specific Kafka topics."""
    
    user_events: str = Field(default="user-events", description="User lifecycle events")
    login_events: str = Field(default="login-events", description="Login/logout events")
    permission_changes: str = Field(default="permission-changes", description="RBAC changes")
    session_events: str = Field(default="session-events", description="Session events")


class KafkaConfig(BaseModel):
    """Kafka configuration."""

    bootstrap_servers: str = Field(
        default="kafka:9092",
        description="Kafka bootstrap servers (comma-separated)",
    )
    
    # Producer settings
    producer_acks: str = Field(default="all", description="Producer acks setting")
    producer_retries: int = Field(default=3, description="Producer retry count")
    producer_timeout_ms: int = Field(default=30000, description="Producer timeout in ms")
    
    # Consumer settings
    consumer_group_id: Optional[str] = Field(
        default=None,
        description="Consumer group ID (defaults to service name)",
    )
    consumer_auto_offset_reset: str = Field(
        default="earliest",
        description="Auto offset reset (earliest/latest)",
    )
    consumer_enable_auto_commit: bool = Field(
        default=True,
        description="Enable auto commit",
    )
    
    # Security (optional)
    security_protocol: str = Field(default="PLAINTEXT", description="Security protocol")
    sasl_mechanism: Optional[str] = Field(default=None, description="SASL mechanism")
    sasl_username: Optional[str] = Field(default=None, description="SASL username")
    sasl_password: Optional[str] = Field(default=None, description="SASL password")
    
    # Topics configuration
    topics: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional topic mappings",
    )

    def get_producer_config(self) -> dict:
        """Get Kafka producer configuration."""
        config = {
            "bootstrap_servers": self.bootstrap_servers.split(","),
            "acks": self.producer_acks,
            "retries": self.producer_retries,
            "request_timeout_ms": self.producer_timeout_ms,
        }
        
        if self.security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.security_protocol
            if self.sasl_mechanism:
                config["sasl_mechanism"] = self.sasl_mechanism
                config["sasl_plain_username"] = self.sasl_username
                config["sasl_plain_password"] = self.sasl_password
        
        return config

    def get_consumer_config(self, group_id: Optional[str] = None) -> dict:
        """Get Kafka consumer configuration."""
        config = {
            "bootstrap_servers": self.bootstrap_servers.split(","),
            "group_id": group_id or self.consumer_group_id,
            "auto_offset_reset": self.consumer_auto_offset_reset,
            "enable_auto_commit": self.consumer_enable_auto_commit,
        }
        
        if self.security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.security_protocol
            if self.sasl_mechanism:
                config["sasl_mechanism"] = self.sasl_mechanism
                config["sasl_plain_username"] = self.sasl_username
                config["sasl_plain_password"] = self.sasl_password
        
        return config
