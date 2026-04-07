"""
Integration tests for CRM Service
"""
import requests
import uuid

BASE_URL = "http://localhost:8005"

class TestHealthEndpoints:
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health/")
        assert response.status_code == 200

class TestCompanyEndpoints:
    def test_list_companies_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/contacts/companies/")
        assert response.status_code in [401, 403, 404]

class TestContactEndpoints:
    def test_list_contacts_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/contacts/")
        assert response.status_code in [401, 403]

class TestLeadEndpoints:
    def test_list_leads_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/pipeline/leads/")
        assert response.status_code in [401, 403, 404]

class TestOpportunityEndpoints:
    def test_list_opportunities_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/pipeline/opportunities/")
        assert response.status_code in [401, 403, 404]

class TestActivityEndpoints:
    def test_list_activities_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/sales/activities/")
        assert response.status_code in [401, 403, 404]

class TestCampaignEndpoints:
    def test_list_campaigns_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/crm/campaigns/")
        assert response.status_code in [401, 403]
