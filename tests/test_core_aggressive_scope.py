"""
Unit tests for engine.core.aggressive_scope module.
"""
import pytest
import asyncio

from engine.core.aggressive_scope import AggressiveScope


class TestAggressiveScope:
    """Tests for AggressiveScope class."""
    
    def test_initialization(self):
        """Test scope initialization."""
        scope = AggressiveScope(primary_target="test.example.com")
        
        assert scope.primary_target == "test.example.com"
        assert isinstance(scope.peripheral_systems, set)
    
    def test_validate_target_valid(self):
        """Test target validation with valid target."""
        scope = AggressiveScope()
        result = scope.validate_target("example.com", authorization_required=False)
        
        assert result["validated"] is True
        assert "validation_checks" in result
    
    def test_validate_target_invalid(self):
        """Test target validation with invalid target."""
        scope = AggressiveScope()
        result = scope.validate_target("", authorization_required=False)
        
        assert result["validated"] is False
        assert len(result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_identify_peripheral_systems(self):
        """Test peripheral system identification."""
        scope = AggressiveScope()
        result = await scope.identify_peripheral_systems("example.com")
        
        assert "primary_target" in result
        assert "peripheral_systems" in result
        assert "dependencies" in result
    
    @pytest.mark.asyncio
    async def test_analyze_trust_boundaries(self):
        """Test trust boundary analysis."""
        scope = AggressiveScope()
        result = await scope.analyze_trust_boundaries("example.com")
        
        assert "target" in result
        assert "trust_boundaries_identified" in result
    
    @pytest.mark.asyncio
    async def test_expand_attack_surface(self):
        """Test attack surface expansion."""
        scope = AggressiveScope()
        result = await scope.expand_attack_surface("example.com")
        
        assert "target" in result
        assert "entry_points" in result
        assert "technologies" in result
    
    def test_expand_scope_boundaries(self):
        """Test scope boundary expansion."""
        scope = AggressiveScope()
        targets = scope.expand_scope_boundaries("example.com")
        
        assert len(targets) > 1
        assert "example.com" in targets
    
    def test_add_peripheral_system(self):
        """Test adding peripheral system."""
        scope = AggressiveScope()
        scope.add_peripheral_system("api.example.com")
        
        assert "api.example.com" in scope.peripheral_systems
    
    def test_add_security_dependency(self):
        """Test adding security dependency."""
        scope = AggressiveScope()
        dependency = {"name": "CDN", "type": "external"}
        scope.add_security_dependency(dependency)
        
        assert len(scope.security_dependencies) == 1
