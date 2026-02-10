"""ServiceNow integration provider skeleton with mock mode."""
import time
from typing import Any, Dict, Optional

import httpx

from finops_common import get_logger

from .base import IntegrationProvider, ProviderResponse

logger = get_logger(__name__)


class ServiceNowProvider(IntegrationProvider):
    """ServiceNow provider skeleton with mock mode support."""

    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None):
        """Initialize ServiceNow provider."""
        super().__init__(config, credentials)
        self.instance_url = config.get("instance_url", "")
        self.table = config.get("table", "incident")  # Default to incidents
        self.mock_mode = config.get("mock_mode", True)  # Default to mock mode
        
        # Authentication
        self.username = credentials.get("username") if credentials else None
        self.password = credentials.get("password") if credentials else None

    async def send(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Create ServiceNow incident or update record."""
        action = payload.get("action", "create_incident")
        
        if action == "create_incident":
            return await self._create_incident(payload)
        elif action == "update_incident":
            return await self._update_incident(payload)
        else:
            return ProviderResponse(
                success=False,
                error_message=f"Unknown action: {action}"
            )

    async def _create_incident(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Create a ServiceNow incident."""
        start_time = time.time()
        
        short_description = payload.get("short_description", "")
        description = payload.get("description", "")
        urgency = payload.get("urgency", "3")  # 1=High, 2=Medium, 3=Low
        impact = payload.get("impact", "3")
        category = payload.get("category", "software")
        
        if not short_description:
            return ProviderResponse(
                success=False,
                error_message="Short description is required"
            )
        
        # Mock mode - simulate success without making real API call
        if self.mock_mode:
            logger.info(f"[MOCK] Creating ServiceNow incident: {short_description}")
            mock_sys_id = "mock-incident-12345"
            mock_number = "INC0012345"
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ProviderResponse(
                success=True,
                response_data={
                    "sys_id": mock_sys_id,
                    "number": mock_number,
                    "short_description": short_description,
                    "state": "1",  # New
                    "mock": True
                },
                external_id=mock_number,
                external_url=f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={mock_sys_id}",
                duration_ms=duration_ms
            )
        
        # Real mode - make actual API call
        if not self.instance_url:
            return ProviderResponse(
                success=False,
                error_message="ServiceNow instance_url must be configured"
            )
        
        if not self.username or not self.password:
            return ProviderResponse(
                success=False,
                error_message="ServiceNow credentials (username, password) required"
            )
        
        try:
            incident_data = {
                "short_description": short_description,
                "description": description,
                "urgency": urgency,
                "impact": impact,
                "category": category,
                "caller_id": self.username  # Use authenticated user as caller
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.instance_url}/api/now/table/{self.table}",
                    json=incident_data,
                    auth=(self.username, self.password),
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    timeout=30
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 201:
                    result = response.json().get("result", {})
                    sys_id = result.get("sys_id")
                    number = result.get("number")
                    
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data=result,
                        external_id=number,
                        external_url=f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}",
                        duration_ms=duration_ms
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"ServiceNow API error: {response.text}",
                        duration_ms=duration_ms
                    )
                    
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"ServiceNow API error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def _update_incident(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Update existing ServiceNow incident."""
        start_time = time.time()
        
        sys_id = payload.get("sys_id", "")
        update_fields = payload.get("fields", {})
        
        if not sys_id:
            return ProviderResponse(
                success=False,
                error_message="sys_id is required for update"
            )
        
        # Mock mode
        if self.mock_mode:
            logger.info(f"[MOCK] Updating ServiceNow incident: {sys_id}")
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ProviderResponse(
                success=True,
                response_data={
                    "sys_id": sys_id,
                    "updated_fields": update_fields,
                    "mock": True
                },
                external_id=sys_id,
                external_url=f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}",
                duration_ms=duration_ms
            )
        
        # Real mode - make actual API call
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.instance_url}/api/now/table/{self.table}/{sys_id}",
                    json=update_fields,
                    auth=(self.username, self.password),
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    timeout=30
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    result = response.json().get("result", {})
                    
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data=result,
                        external_id=sys_id,
                        external_url=f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}",
                        duration_ms=duration_ms
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"ServiceNow API error: {response.text}",
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
        """Verify ServiceNow connection."""
        if self.mock_mode:
            return ProviderResponse(
                success=True,
                response_data={"mock": True, "message": "Mock mode enabled"}
            )
        
        if not self.instance_url:
            return ProviderResponse(
                success=False,
                error_message="ServiceNow instance_url not configured"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                # Test with a simple table query
                response = await client.get(
                    f"{self.instance_url}/api/now/table/sys_user?sysparm_limit=1",
                    auth=(self.username, self.password),
                    headers={"Accept": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return ProviderResponse(
                        success=True,
                        http_status=response.status_code,
                        response_data={"message": "ServiceNow connection verified"}
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        http_status=response.status_code,
                        error_message=f"ServiceNow verification failed: HTTP {response.status_code}"
                    )
        except Exception as e:
            return ProviderResponse(
                success=False,
                error_message=f"ServiceNow verification error: {str(e)}"
            )

    async def test(self, payload: Optional[Dict[str, Any]] = None) -> ProviderResponse:
        """Test ServiceNow with sample incident creation."""
        test_payload = payload or {
            "action": "create_incident",
            "short_description": "Test Incident from FinOps Platform",
            "description": "This is a test incident to verify ServiceNow integration",
            "urgency": "3",  # Low
            "impact": "3",  # Low
            "category": "inquiry"
        }
        
        return await self.send(test_payload)
