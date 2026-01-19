"""
Unit tests for engine.reporting.generator module.
"""
import pytest
from pathlib import Path

from engine.reporting.generator import ReportGenerator
from engine.storage.session_store import SessionStore


class TestReportGenerator:
    """Tests for ReportGenerator class."""
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create report generator with temp directory."""
        output_dir = temp_dir / "reports"
        template_dir = temp_dir / "templates"
        return ReportGenerator(
            template_dir=str(template_dir),
            output_dir=str(output_dir)
        )
    
    @pytest.fixture
    def sample_assessment_data(self, sample_session_data, sample_findings):
        """Sample assessment data for reporting."""
        data = sample_session_data.copy()
        data["findings"] = sample_findings
        data["risk_score"] = 0.6
        data["recommendations"] = [
            {"title": "Fix Headers", "description": "Add security headers"}
        ]
        return data
    
    def test_generate_executive_report_html(self, generator, sample_assessment_data):
        """Test generating executive report in HTML format."""
        report_path = generator.generate_executive_report(sample_assessment_data, format="html")
        
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".html"
    
    def test_generate_executive_report_json(self, generator, sample_assessment_data):
        """Test generating executive report in JSON format."""
        report_path = generator.generate_executive_report(sample_assessment_data, format="json")
        
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".json"
    
    def test_generate_executive_report_markdown(self, generator, sample_assessment_data):
        """Test generating executive report in Markdown format."""
        report_path = generator.generate_executive_report(sample_assessment_data, format="markdown")
        
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".md"
    
    def test_generate_technical_report(self, generator, sample_assessment_data):
        """Test generating technical report."""
        report_path = generator.generate_technical_report(sample_assessment_data, format="html")
        
        assert Path(report_path).exists()
        assert report_path.endswith(".html")
    
    def test_create_interactive_dashboard(self, generator, sample_assessment_data):
        """Test creating interactive dashboard."""
        dashboard_path = generator.create_interactive_dashboard(sample_assessment_data)
        
        assert Path(dashboard_path).exists()
        assert dashboard_path.endswith(".html")
    
    def test_generate_compliance_report(self, generator, sample_assessment_data):
        """Test generating compliance report."""
        report_path = generator.generate_compliance_report(sample_assessment_data, "NIST")
        
        assert Path(report_path).exists()
