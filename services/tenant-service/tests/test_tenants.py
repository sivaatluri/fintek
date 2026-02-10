"""Tests for tenant CRUD operations with org_id enforcement."""
import pytest


@pytest.mark.asyncio
async def test_create_tenant(client, auth_headers, mock_org_id):
    """Test creating a tenant."""
    data = {
        "name": "Test Tenant",
        "description": "A test tenant",
        "settings": {"env": "test"},
    }
    
    response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == data["name"]
    assert result["slug"] == "test-tenant"
    assert result["org_id"] == mock_org_id
    assert result["description"] == data["description"]
    assert result["is_active"] is True


@pytest.mark.asyncio
async def test_create_tenant_without_org_id(client):
    """Test creating tenant without org_id in headers."""
    data = {"name": "No Org Tenant"}
    
    response = client.post("/api/v1/tenants", json=data)
    
    assert response.status_code == 400
    assert "Organization ID required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_tenants(client, auth_headers):
    """Test listing tenants for an organization."""
    # Create test tenants
    for i in range(3):
        data = {"name": f"List Tenant {i}"}
        client.post("/api/v1/tenants", json=data, headers=auth_headers)
    
    response = client.get("/api/v1/tenants", headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 3
    assert all(tenant["org_id"] == auth_headers["X-Org-ID"] for tenant in result)


@pytest.mark.asyncio
async def test_get_tenant(client, auth_headers):
    """Test getting tenant by ID."""
    # Create tenant
    data = {"name": "Get Test Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Get tenant
    response = client.get(f"/api/v1/tenants/{tenant_id}", headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == tenant_id
    assert result["name"] == data["name"]


@pytest.mark.asyncio
async def test_get_tenant_wrong_org(client, auth_headers):
    """Test that tenant from different org is not accessible."""
    # Create tenant with org1
    data = {"name": "Org1 Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Try to access with different org
    wrong_headers = auth_headers.copy()
    wrong_headers["X-Org-ID"] = "different-org-id"
    response = client.get(f"/api/v1/tenants/{tenant_id}", headers=wrong_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tenant(client, auth_headers):
    """Test updating tenant."""
    # Create tenant
    data = {"name": "Update Test Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Update tenant
    update_data = {
        "name": "Updated Tenant Name",
        "description": "Updated description",
    }
    response = client.put(f"/api/v1/tenants/{tenant_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == update_data["name"]
    assert result["description"] == update_data["description"]
    assert result["slug"] == "updated-tenant-name"


@pytest.mark.asyncio
async def test_update_tenant_wrong_org(client, auth_headers):
    """Test that tenant from different org cannot be updated."""
    # Create tenant with org1
    data = {"name": "Org1 Update Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Try to update with different org
    wrong_headers = auth_headers.copy()
    wrong_headers["X-Org-ID"] = "different-org-id"
    update_data = {"name": "Hacked Name"}
    response = client.put(f"/api/v1/tenants/{tenant_id}", json=update_data, headers=wrong_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tenant(client, auth_headers):
    """Test deleting tenant (soft delete)."""
    # Create tenant
    data = {"name": "Delete Test Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Delete tenant
    response = client.delete(f"/api/v1/tenants/{tenant_id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify tenant is not accessible
    get_response = client.get(f"/api/v1/tenants/{tenant_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tenant_wrong_org(client, auth_headers):
    """Test that tenant from different org cannot be deleted."""
    # Create tenant with org1
    data = {"name": "Org1 Delete Tenant"}
    create_response = client.post("/api/v1/tenants", json=data, headers=auth_headers)
    tenant_id = create_response.json()["id"]
    
    # Try to delete with different org
    wrong_headers = auth_headers.copy()
    wrong_headers["X-Org-ID"] = "different-org-id"
    response = client.delete(f"/api/v1/tenants/{tenant_id}", headers=wrong_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tenant_pagination(client, auth_headers):
    """Test tenant pagination."""
    # Create 15 tenants
    for i in range(15):
        data = {"name": f"Pagination Tenant {i:02d}"}
        client.post("/api/v1/tenants", json=data, headers=auth_headers)
    
    # Get first page
    response1 = client.get("/api/v1/tenants?skip=0&limit=10", headers=auth_headers)
    assert response1.status_code == 200
    result1 = response1.json()
    assert len(result1) == 10
    
    # Get second page
    response2 = client.get("/api/v1/tenants?skip=10&limit=10", headers=auth_headers)
    assert response2.status_code == 200
    result2 = response2.json()
    assert len(result2) >= 5
