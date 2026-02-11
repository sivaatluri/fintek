"""Jira integration provider skeleton with mock mode."""
import time
from typing import Any, Dict, Optional

import httpx

from finops_common import get_logger

from .base import IntegrationProvider, ProviderResponse

logger = get_logger(__name__)


class JiraProvider(IntegrationProvider):
    """Jira provider skeleton with mock mode support."""

    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None):
        """Initialize Jira provider."""
        super().__init__(config, credentials)
        self.base_url = config.get("base_url", "")
        self.project_key = config.get("project_key", "")
        self.issue_type = config.get("issue_type", "Task")
        self.mock_mode = config.get("mock_mode", True)  # Default to mock mode
        
        # Authentication
        self.username = credentials.get("username") if credentials else None
        self.api_token = credentials.get("api_token") if credentials else None

    async def send(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Create Jira issue or add comment."""
        action = payload.get("action", "create_issue")
        
        if action == "create_issue":
            return await self._create_issue(payload)
        elif action == "add_comment":
            return await self._add_comment(payload)
        else:
            return ProviderResponse(
                success=False,
                error_message=f"Unknown action: {action}"
            )

    async def _create_issue(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Create a Jira issue."""
        start_time = time.time()
        
        summary = payload.get("summary", "")
        description = payload.get("description", "")
        priority = payload.get("priority", "Medium")
        
        if not summary:
            return ProviderResponse(
                success=False,
                error_message="Issue summary is required"
            )
        
        # Mock mode - simulate success without making real API call
        if self.mock_mode:
            logger.info(f"[MOCK] Creating Jira issue: {summary}")
            mock_issue_key = f"{self.project_key or 'MOCK'}-12345"
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ProviderResponse(
                success=True,
                response_data={
                    "key": mock_issue_key,
                    "self": f"{self.base_url}/browse/{mock_issue_key}",
                    "summary": summary,
                    "mock": True
                },
                external_id=mock_issue_key,
                external_url=f"{self.base_url}/browse/{mock_issue_key}",
                duration_ms=duration_ms
            )
        
        # Real mode - make actual API call
        if not self.base_url or not self.project_key:
            return ProviderResponse(
                success=False,
                error_message="Jira base_url and project_key must be configured"
            )
        
        if not self.username or not self.api_token:
            return ProviderResponse(
                success=False,
                error_message="Jira credentials (username, api_token) required"
            )
        
        try:
            issue_data = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": self.issue_type},
                    "priority": {"name": priority}
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/3/issue",
                    json=issue_data,
                    auth=(self.username, self.api_token),
                    timeout=30
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 201:
                    result = response.json()
                    issue_key = result.get("key")
                    
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data=result,
                        external_id=issue_key,
                        external_url=f"{self.base_url}/browse/{issue_key}",
                        duration_ms=duration_ms
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"Jira API error: {response.text}",
                        duration_ms=duration_ms
                    )
                    
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Jira API error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def _add_comment(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Add comment to existing Jira issue."""
        start_time = time.time()
        
        issue_key = payload.get("issue_key", "")
        comment_text = payload.get("comment", "")
        
        if not issue_key or not comment_text:
            return ProviderResponse(
                success=False,
                error_message="issue_key and comment are required"
            )
        
        # Mock mode
        if self.mock_mode:
            logger.info(f"[MOCK] Adding comment to {issue_key}")
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ProviderResponse(
                success=True,
                response_data={
                    "id": "mock-comment-id",
                    "issue_key": issue_key,
                    "comment": comment_text,
                    "mock": True
                },
                external_id=issue_key,
                external_url=f"{self.base_url}/browse/{issue_key}",
                duration_ms=duration_ms
            )
        
        # Real mode - make actual API call
        try:
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": comment_text}
                            ]
                        }
                    ]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
                    json=comment_data,
                    auth=(self.username, self.api_token),
                    timeout=30
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 201:
                    result = response.json()
                    
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data=result,
                        external_id=issue_key,
                        external_url=f"{self.base_url}/browse/{issue_key}",
                        duration_ms=duration_ms
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"Jira API error: {response.text}",
                        duration_ms=duration_ms
                    )
                    
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ProviderResponse(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def verify(self) -> ProviderResponse:
        """Verify Jira connection."""
        if self.mock_mode:
            return ProviderResponse(
                success=True,
                response_data={"mock": True, "message": "Mock mode enabled"}
            )
        
        if not self.base_url:
            return ProviderResponse(
                success=False,
                error_message="Jira base_url not configured"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/myself",
                    auth=(self.username, self.api_token),
                    timeout=10
                )
                
                if response.status_code == 200:
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data=response.json()
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"Jira verification failed: HTTP {response.status_code}"
                    )
        except Exception as e:
            return ProviderResponse(
                success=False,
                error_message=f"Jira verification error: {str(e)}"
            )

    async def test(self, payload: Optional[Dict[str, Any]] = None) -> ProviderResponse:
        """Test Jira with sample issue creation."""
        test_payload = payload or {
            "action": "create_issue",
            "summary": "Test Issue from FinOps Platform",
            "description": "This is a test issue to verify Jira integration",
            "priority": "Low"
        }
        
        return await self.send(test_payload)
