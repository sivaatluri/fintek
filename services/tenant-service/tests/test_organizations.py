"""Tests for organization CRUD operations."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_organization(client, auth_headers):
    """Test creating an organization."""
    data = {
        "name": "Test Organization",
        "description": "A test organization",
        "industry": "Technology",
        "settings": {"key": "value"},
    }
    
    response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == data["name"]
    assert result["slug"] == "test-organization"
    assert result["description"] == data["description"]
    assert result["industry"] == data["industry"]
    assert result["is_active"] is True
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_create_organization_duplicate_slug(client, auth_headers):
    """Test creating organizations with duplicate names generates unique slugs."""
    data = {
        "name": "Duplicate Org",
        "description": "First org",
    }
    
    # Create first org
    response1 = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    assert response1.status_code == 201
    result1 = response1.json()
    assert result1["slug"] == "duplicate-org"
    
    # Create second org with same name
    data["description"] = "Second org"
    response2 = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    assert response2.status_code == 201
    result2 = response2.json()
    assert result2["slug"] == "duplicate-org-1"


@pytest.mark.asyncio
async def test_list_organizations(client, auth_headers):
    """Test listing organizations."""
    # Create test orgs
    for i in range(3):
        data = {"name": f"Test Org {i}"}
        client.post("/api/v1/orgs", json=data, headers=auth_headers)
    
    response = client.get("/api/v1/orgs", headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 3
    assert all("id" in org for org in result)
    assert all("name" in org for org in result)


@pytest.mark.asyncio
async def test_get_organization(client, auth_headers):
    """Test getting organization by ID."""
    # Create org
    data = {"name": "Get Test Org"}
    create_response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    org_id = create_response.json()["id"]
    
    # Get org
    response = client.get(f"/api/v1/orgs/{org_id}", headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == org_id
    assert result["name"] == data["name"]


@pytest.mark.asyncio
async def test_get_organization_not_found(client, auth_headers):
    """Test getting non-existent organization."""
    response = client.get("/api/v1/orgs/nonexistent-id", headers=auth_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_organization(client, auth_headers):
    """Test updating organization."""
    # Create org
    data = {"name": "Update Test Org"}
    create_response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    org_id = create_response.json()["id"]
    
    # Update org
    update_data = {
        "name": "Updated Org Name",
        "description": "Updated description",
        "industry": "Finance",
    }
    response = client.put(f"/api/v1/orgs/{org_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == update_data["name"]
    assert result["description"] == update_data["description"]
    assert result["industry"] == update_data["industry"]
    assert result["slug"] == "updated-org-name"


@pytest.mark.asyncio
async def test_delete_organization(client, auth_headers):
    """Test deleting organization (soft delete)."""
    # Create org
    data = {"name": "Delete Test Org"}
    create_response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    org_id = create_response.json()["id"]
    
    # Delete org
    response = client.delete(f"/api/v1/orgs/{org_id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify org is not accessible
    get_response = client.get(f"/api/v1/orgs/{org_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_organization_not_found(client, auth_headers):
    """Test deleting non-existent organization."""
    response = client.delete("/api/v1/orgs/nonexistent-id", headers=auth_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_organization_pagination(client, auth_headers):
    """Test organization pagination."""
    # Create 15 orgs
    for i in range(15):
        data = {"name": f"Pagination Org {i:02d}"}
        client.post("/api/v1/orgs", json=data, headers=auth_headers)
    
    # Get first page
    response1 = client.get("/api/v1/orgs?skip=0&limit=10", headers=auth_headers)
    assert response1.status_code == 200
    result1 = response1.json()
    assert len(result1) == 10
    
    # Get second page
    response2 = client.get("/api/v1/orgs?skip=10&limit=10", headers=auth_headers)
    assert response2.status_code == 200
    result2 = response2.json()
    assert len(result2) >= 5


@pytest.mark.asyncio
async def test_organization_validation(client, auth_headers):
    """Test organization validation."""
    # Test empty name
    data = {"name": ""}
    response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    assert response.status_code == 422
    
    # Test missing name
    data = {"description": "No name"}
    response = client.post("/api/v1/orgs", json=data, headers=auth_headers)
    assert response.status_code == 422
