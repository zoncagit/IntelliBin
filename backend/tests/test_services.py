"""
Unit tests for IntelliBin services
"""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.state import StateManager
from app.services.classification import ClassificationService
from app.services.compatibility import CompatibilityService
from app.services.routing import RoutingService
from app.models.responses import RouteRequest, RiskLevel


class TestClassification:
    """Tests for the classification service"""
    
    @pytest.fixture
    def service(self):
        state = StateManager()
        state.reset()
        return ClassificationService()
    
    def test_classify_by_exact_name(self, service):
        result = service.classify("Acetone")
        assert result is not None
        assert result["name"] == "Acetone"
        assert result["category"] == "Solvent"
    
    def test_classify_by_alias(self, service):
        result = service.classify("NaOH")
        assert result is not None
        assert result["name"] == "Sodium Hydroxide"
        assert result["category"] == "Base"
    
    def test_classify_case_insensitive(self, service):
        result = service.classify("ACETONE")
        assert result is not None
        assert result["name"] == "Acetone"
    
    def test_classify_unknown_returns_none(self, service):
        result = service.classify("Unknown Chemical XYZ")
        assert result is None
    
    def test_get_waste_stream(self, service):
        substance = service.classify("Chloroform")
        stream = service.get_waste_stream(substance)
        assert stream == "HalogenatedSolvent"
    
    def test_search_substances(self, service):
        results = service.search_substances("acid")
        assert len(results) > 0


class TestCompatibility:
    """Tests for the compatibility service"""
    
    @pytest.fixture
    def service(self):
        state = StateManager()
        state.reset()
        return CompatibilityService()
    
    @pytest.fixture
    def state(self):
        s = StateManager()
        s.reset()
        return s
    
    def test_same_category_compatible(self, service, state):
        acid_substance = state.substances["hcl-dilute"]
        acid_container = state.containers["ACID-001"]
        
        is_compatible, issue = service.check_compatibility(acid_substance, acid_container)
        
        assert is_compatible is True
        assert issue is None
    
    def test_oxidizer_incompatible_with_solvent(self, service, state):
        oxidizer = state.substances["h2o2-30"]
        solvent_container = state.containers["SOLV-001"]
        
        is_compatible, issue = service.check_compatibility(oxidizer, solvent_container)
        
        assert is_compatible is False
        assert issue is not None


class TestRouting:
    """Tests for the routing service"""
    
    @pytest.fixture
    def service(self):
        state = StateManager()
        state.reset()
        return RoutingService()
    
    def test_route_solvent_success(self, service):
        request = RouteRequest(
            substance="Acetone",
            quantity_ml=100,
            concentration="Pure"
        )
        response = service.route(request)
        
        assert response.success is True
        assert response.classified_as.category == "Solvent"
        assert response.routed_to.container_id == "SOLV-001"
        assert response.safety_status == RiskLevel.SAFE
    
    def test_route_unknown_fails(self, service):
        request = RouteRequest(
            substance="Mystery Chemical",
            quantity_ml=100,
            concentration="Pure"
        )
        response = service.route(request)
        
        assert response.success is False
        assert response.safety_status == RiskLevel.DANGER
    
    def test_route_metal_to_metal_container(self, service):
        request = RouteRequest(
            substance="Sodium Metal",
            quantity_ml=10,
            concentration="Pure"
        )
        response = service.route(request)
        
        assert response.success is True
        assert response.routed_to.container_id == "METAL-001"


class TestStateManager:
    """Tests for the state manager"""
    
    @pytest.fixture
    def state(self):
        s = StateManager()
        s.reset()
        return s
    
    def test_get_all_containers(self, state):
        containers = state.get_all_containers()
        assert len(containers) > 0
    
    def test_get_containers_by_stream(self, state):
        containers = state.get_containers_by_stream("AqueousAcid")
        assert len(containers) >= 1
        assert all(c["waste_stream"] == "AqueousAcid" for c in containers)
    
    def test_update_container(self, state):
        initial_fill = state.containers["SOLV-001"]["current_fill_ml"]
        
        state.update_container(
            container_id="SOLV-001",
            substance_name="Acetone",
            category="Solvent",
            quantity_ml=100,
            concentration="Pure"
        )
        
        new_fill = state.containers["SOLV-001"]["current_fill_ml"]
        assert new_fill == initial_fill + 100
    
    def test_reset(self, state):
        # Make some changes
        state.update_container(
            container_id="SOLV-001",
            substance_name="Acetone",
            category="Solvent",
            quantity_ml=500,
            concentration="Pure"
        )
        
        # Reset
        state.reset()
        
        # Should be back to initial state
        assert len(state.disposal_log) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
