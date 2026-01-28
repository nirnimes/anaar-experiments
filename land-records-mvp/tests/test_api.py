"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthAndMetadata:
    """Test health check and metadata endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "records_count" in data
        assert data["status"] == "healthy"

    def test_metadata(self):
        """Test metadata endpoint"""
        response = client.get("/api/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "localities" in data
        assert "total_records" in data
        assert "data_sources" in data
        assert len(data["localities"]) == 4


class TestPropertySearch:
    """Test property search functionality"""

    def test_search_all_properties(self):
        """Test searching all properties without filters"""
        response = client.get("/api/properties/search")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "properties" in data
        assert data["total"] > 0

    def test_search_by_locality(self):
        """Test searching by locality"""
        response = client.get("/api/properties/search?locality=Greater Kailash I")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert all(p["locality"] == "Greater Kailash I" for p in data["properties"])

    def test_search_by_encumbrance_status(self):
        """Test searching by encumbrance status"""
        response = client.get("/api/properties/search?encumbrance_status=Clear")
        assert response.status_code == 200
        data = response.json()
        if data["total"] > 0:
            assert all(p["encumbrance_status"] == "Clear" for p in data["properties"])

    def test_search_by_area_range(self):
        """Test searching by area range"""
        response = client.get("/api/properties/search?min_area=200&max_area=400")
        assert response.status_code == 200
        data = response.json()
        if data["total"] > 0:
            assert all(200 <= p["area_sqm"] <= 400 for p in data["properties"])

    def test_search_pagination(self):
        """Test search pagination"""
        response = client.get("/api/properties/search?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["properties"]) <= 5

    def test_search_invalid_locality(self):
        """Test search with invalid locality"""
        response = client.get("/api/properties/search?locality=Invalid")
        assert response.status_code == 200  # Should return empty results
        data = response.json()
        assert data["total"] == 0


class TestPropertyDetail:
    """Test property detail endpoint"""

    def test_get_property_by_id(self):
        """Test getting property by ID"""
        # First, get a valid property ID
        search_response = client.get("/api/properties/search?page_size=1")
        properties = search_response.json()["properties"]
        if properties:
            property_id = properties[0]["id"]

            response = client.get(f"/api/properties/{property_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == property_id
            assert "plot_number" in data
            assert "locality" in data

    def test_get_nonexistent_property(self):
        """Test getting non-existent property"""
        response = client.get("/api/properties/99999")
        assert response.status_code == 404


class TestPropertyComparison:
    """Test property comparison functionality"""

    def test_compare_two_properties(self):
        """Test comparing two properties"""
        # Get two property IDs
        search_response = client.get("/api/properties/search?page_size=2")
        properties = search_response.json()["properties"]

        if len(properties) >= 2:
            ids = [properties[0]["id"], properties[1]["id"]]

            response = client.post(
                "/api/properties/compare",
                json={"property_ids": ids}
            )
            assert response.status_code == 200
            data = response.json()
            assert "properties" in data
            assert "comparison_matrix" in data
            assert "insights" in data
            assert len(data["properties"]) == 2

    def test_compare_invalid_count(self):
        """Test comparison with invalid number of properties"""
        response = client.post(
            "/api/properties/compare",
            json={"property_ids": [1]}
        )
        assert response.status_code == 400

    def test_compare_too_many_properties(self):
        """Test comparison with too many properties"""
        response = client.post(
            "/api/properties/compare",
            json={"property_ids": [1, 2, 3, 4, 5]}
        )
        assert response.status_code == 400


class TestLocalityStatistics:
    """Test locality statistics endpoint"""

    def test_get_locality_stats(self):
        """Test getting statistics for a locality"""
        response = client.get("/api/statistics/locality/Greater Kailash I")
        assert response.status_code == 200
        data = response.json()
        assert "locality" in data
        assert "total_properties" in data
        assert "encumbrance_distribution" in data
        assert "property_type_distribution" in data

    def test_get_invalid_locality_stats(self):
        """Test getting statistics for invalid locality"""
        response = client.get("/api/statistics/locality/Invalid")
        assert response.status_code == 400

    def test_get_summary_statistics(self):
        """Test getting summary statistics"""
        response = client.get("/api/statistics/summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0


class TestPropertyCreation:
    """Test property creation endpoint"""

    def test_create_property(self):
        """Test creating a new property"""
        new_property = {
            "plot_number": "TEST-999",
            "locality": "Greater Kailash I",
            "area_sqm": 300.0,
            "encumbrance_status": "Clear",
            "property_type": "Residential",
            "data_source": "Manual Entry",
            "last_verified": "2026-01-27"
        }

        response = client.post("/api/properties", json=new_property)
        assert response.status_code == 201
        data = response.json()
        assert data["plot_number"] == "TEST-999"
        assert data["locality"] == "Greater Kailash I"

    def test_create_duplicate_property(self):
        """Test creating duplicate property"""
        property_data = {
            "plot_number": "DUP-TEST",
            "locality": "Greater Kailash I",
            "area_sqm": 300.0,
            "encumbrance_status": "Clear",
            "property_type": "Residential",
            "data_source": "Manual Entry",
            "last_verified": "2026-01-27"
        }

        # Create first time
        response1 = client.post("/api/properties", json=property_data)
        assert response1.status_code == 201

        # Try to create again - should fail
        response2 = client.post("/api/properties", json=property_data)
        assert response2.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
