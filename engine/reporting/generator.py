"""
Advanced report generation engine for PROJEK DENGKIS.
Transforms assessment findings into professional reports in multiple formats.
"""
from jinja2 import Environment, FileSystemLoader, Template
import markdown
from datetime import datetime
import os
import json
from typing import Dict, List, Optional, Any
import base64
from pathlib import Path


class ReportGenerator:
    """
    Advanced report generation engine that transforms assessment findings
    into professional, customizable reports in multiple formats.
    Implements template-based rendering with dynamic content injection.
    """
    
    def __init__(self, template_dir: str = 'templates', output_dir: str = 'reports'):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        
        # Create directories if they don't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        if self.template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        else:
            self.env = Environment()
        
        self.custom_css = """
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }
        .header { background-color: #073B4C; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .critical { color: #FF4B4B; font-weight: bold; }
        .high { color: #FF8C42; font-weight: bold; }
        .medium { color: #FFD166; font-weight: bold; }
        .low { color: #06D6A0; font-weight: bold; }
        .info { color: #118AB2; font-weight: bold; }
        .finding { border-left: 4px solid #118AB2; padding: 10px; margin: 10px 0; background-color: #f9f9f9; }
        .finding.critical { border-left-color: #FF4B4B; }
        .finding.high { border-left-color: #FF8C42; }
        .finding.medium { border-left-color: #FFD166; }
        .finding.low { border-left-color: #06D6A0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #073B4C; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .recommendation { background-color: #fff3cd; padding: 10px; border-left: 4px solid #FFD166; margin: 10px 0; }
        """
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default report templates if they don't exist."""
        if not (self.template_dir / 'executive.html').exists():
            self._create_executive_template()
        if not (self.template_dir / 'technical.html').exists():
            self._create_technical_template()
        if not (self.template_dir / 'dashboard.html').exists():
            self._create_dashboard_template()
    
    def _create_executive_template(self):
        """Create default executive report template."""
        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>Executive Security Assessment Report</title>
    <style>{{ css }}</style>
</head>
<body>
    <div class="header">
        <h1>Executive Security Assessment Report</h1>
        <p>Generated: {{ timestamp }}</p>
        <p>Target: {{ target }}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Overall Risk Score:</strong> {{ overall_risk_score }}</p>
        <p><strong>Total Findings:</strong> {{ total_findings }}</p>
        <p><strong>Critical Findings:</strong> <span class="critical">{{ critical_count }}</span></p>
        <p><strong>High Findings:</strong> <span class="high">{{ high_count }}</span></p>
        <p><strong>Medium Findings:</strong> <span class="medium">{{ medium_count }}</span></p>
        <p><strong>Low Findings:</strong> <span class="low">{{ low_count }}</span></p>
    </div>
    
    <h2>Key Findings</h2>
    {% for finding in key_findings %}
    <div class="finding {{ finding.severity }}">
        <h3>{{ finding.title }}</h3>
        <p><strong>Severity:</strong> <span class="{{ finding.severity }}">{{ finding.severity }}</span></p>
        <p>{{ finding.description }}</p>
    </div>
    {% endfor %}
    
    <h2>Strategic Recommendations</h2>
    {% for rec in recommendations %}
    <div class="recommendation">
        <p><strong>{{ rec.title }}</strong></p>
        <p>{{ rec.description }}</p>
    </div>
    {% endfor %}
</body>
</html>"""
        (self.template_dir / 'executive.html').write_text(template_content)
    
    def _create_technical_template(self):
        """Create default technical report template."""
        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>Technical Security Assessment Report</title>
    <style>{{ css }}</style>
</head>
<body>
    <div class="header">
        <h1>Technical Security Assessment Report</h1>
        <p>Generated: {{ timestamp }}</p>
        <p>Target: {{ target }}</p>
        <p>Session ID: {{ session_id }}</p>
    </div>
    
    <h2>Assessment Overview</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Findings</td><td>{{ total_findings }}</td></tr>
        <tr><td>Critical</td><td><span class="critical">{{ critical_count }}</span></td></tr>
        <tr><td>High</td><td><span class="high">{{ high_count }}</span></td></tr>
        <tr><td>Medium</td><td><span class="medium">{{ medium_count }}</span></td></tr>
        <tr><td>Low</td><td><span class="low">{{ low_count }}</span></td></tr>
    </table>
    
    <h2>Detailed Findings</h2>
    {% for finding in findings %}
    <div class="finding {{ finding.severity }}">
        <h3>{{ finding.title }}</h3>
        <p><strong>ID:</strong> {{ finding.id }}</p>
        <p><strong>Severity:</strong> <span class="{{ finding.severity }}">{{ finding.severity }}</span></p>
        <p><strong>Category:</strong> {{ finding.category }}</p>
        <p><strong>Description:</strong> {{ finding.description }}</p>
        {% if finding.recommendation %}
        <p><strong>Recommendation:</strong> {{ finding.recommendation }}</p>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>"""
        (self.template_dir / 'technical.html').write_text(template_content)
    
    def _create_dashboard_template(self):
        """Create default dashboard template."""
        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>Interactive Security Dashboard</title>
    <style>{{ css }}</style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>Interactive Security Dashboard</h1>
        <p>Target: {{ target }}</p>
        <p>Generated: {{ timestamp }}</p>
    </div>
    
    <div id="dashboard-content">
        <h2>Assessment Summary</h2>
        <div class="summary">
            <p><strong>Total Findings:</strong> {{ total_findings }}</p>
            <p><strong>Risk Score:</strong> {{ overall_risk_score }}</p>
        </div>
        
        {% if visualizations %}
        <h2>Visualizations</h2>
        {% for viz in visualizations %}
        <div id="viz-{{ loop.index }}">{{ viz.html | safe }}</div>
        {% endfor %}
        {% endif %}
    </div>
</body>
</html>"""
        (self.template_dir / 'dashboard.html').write_text(template_content)
    
    def generate_executive_report(self, assessment_data: Dict, format: str = 'html') -> str:
        """
        Generate executive summary report with high-level findings,
        risk metrics, and strategic recommendations.
        
        Args:
            assessment_data: Complete assessment data
            format: Output format ('html', 'json', 'markdown')
            
        Returns:
            Path to generated report file
        """
        findings = assessment_data.get('findings', [])
        
        # Calculate summary statistics
        summary = {
            'total_findings': len(findings),
            'critical_count': len([f for f in findings if f.get('severity', '').lower() == 'critical']),
            'high_count': len([f for f in findings if f.get('severity', '').lower() == 'high']),
            'medium_count': len([f for f in findings if f.get('severity', '').lower() == 'medium']),
            'low_count': len([f for f in findings if f.get('severity', '').lower() == 'low']),
            'overall_risk_score': assessment_data.get('risk_score', 0.0),
            'target': assessment_data.get('target', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'key_findings': sorted(findings, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', '').lower(), 4))[:10],
            'recommendations': assessment_data.get('recommendations', [])
        }
        
        if format == 'html':
            return self._generate_html_report('executive.html', summary, 'executive')
        elif format == 'json':
            return self._generate_json_report(summary, 'executive')
        elif format == 'markdown':
            return self._generate_markdown_report(summary, 'executive')
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_technical_report(self, assessment_data: Dict, format: str = 'html') -> str:
        """
        Generate detailed technical report with comprehensive findings,
        evidence, and remediation guidance.
        
        Args:
            assessment_data: Complete assessment data
            format: Output format ('html', 'json', 'markdown')
            
        Returns:
            Path to generated report file
        """
        findings = assessment_data.get('findings', [])
        
        # Prepare technical data
        technical_data = {
            'target': assessment_data.get('target', 'Unknown'),
            'session_id': assessment_data.get('session_id', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'total_findings': len(findings),
            'critical_count': len([f for f in findings if f.get('severity', '').lower() == 'critical']),
            'high_count': len([f for f in findings if f.get('severity', '').lower() == 'high']),
            'medium_count': len([f for f in findings if f.get('severity', '').lower() == 'medium']),
            'low_count': len([f for f in findings if f.get('severity', '').lower() == 'low']),
            'findings': findings,
            'css': self.custom_css
        }
        
        if format == 'html':
            return self._generate_html_report('technical.html', technical_data, 'technical')
        elif format == 'json':
            return self._generate_json_report(technical_data, 'technical')
        elif format == 'markdown':
            return self._generate_markdown_report(technical_data, 'technical')
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_compliance_report(self, assessment_data: Dict, framework: str) -> str:
        """
        Generate compliance-specific report aligned with specified
        security framework (e.g., NIST, ISO 27001, CIS).
        
        Args:
            assessment_data: Complete assessment data
            framework: Compliance framework
            
        Returns:
            Path to generated compliance report
        """
        compliance_data = {
            'target': assessment_data.get('target', 'Unknown'),
            'framework': framework,
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_score': assessment_data.get('compliance_score', 0.0),
            'findings': assessment_data.get('findings', []),
            'recommendations': assessment_data.get('recommendations', [])
        }
        
        # Use technical template for now, can be customized per framework
        return self._generate_html_report('technical.html', compliance_data, f'compliance_{framework}')
    
    def create_interactive_dashboard(self, assessment_data: Dict) -> str:
        """
        Create interactive HTML dashboard with dynamic visualizations
        and filtering capabilities.
        
        Args:
            assessment_data: Complete assessment data
            
        Returns:
            Path to generated dashboard file
        """
        dashboard_data = {
            'target': assessment_data.get('target', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'total_findings': len(assessment_data.get('findings', [])),
            'overall_risk_score': assessment_data.get('risk_score', 0.0),
            'visualizations': assessment_data.get('visualizations', []),
            'css': self.custom_css
        }
        
        return self._generate_html_report('dashboard.html', dashboard_data, 'dashboard')
    
    def _generate_html_report(self, template_name: str, data: Dict, report_type: str) -> str:
        """Generate HTML report from template."""
        try:
            template = self.env.get_template(template_name)
        except:
            # Fallback to inline template
            template = Template(self._get_default_template(report_type))
        
        html_content = template.render(**data, css=self.custom_css)
        
        # Save report
        filename = f"{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        filepath.write_text(html_content)
        
        return str(filepath)
    
    def _generate_json_report(self, data: Dict, report_type: str) -> str:
        """Generate JSON report."""
        filename = f"{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        filepath.write_text(json.dumps(data, indent=2, default=str))
        
        return str(filepath)
    
    def _generate_markdown_report(self, data: Dict, report_type: str) -> str:
        """Generate Markdown report."""
        md_content = f"# {report_type.title()} Report\n\n"
        md_content += f"**Target:** {data.get('target', 'Unknown')}\n\n"
        md_content += f"**Generated:** {data.get('timestamp', 'Unknown')}\n\n"
        md_content += f"**Total Findings:** {data.get('total_findings', 0)}\n\n"
        
        if 'findings' in data:
            md_content += "## Findings\n\n"
            for finding in data['findings']:
                md_content += f"### {finding.get('title', 'Unknown')}\n"
                md_content += f"**Severity:** {finding.get('severity', 'Unknown')}\n\n"
                md_content += f"{finding.get('description', '')}\n\n"
        
        filename = f"{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename
        filepath.write_text(md_content)
        
        return str(filepath)
    
    def _get_default_template(self, report_type: str) -> str:
        """Get default template content."""
        if report_type == 'executive':
            return """<!DOCTYPE html><html><head><title>Executive Report</title><style>{{ css }}</style></head><body><h1>Executive Report</h1><p>{{ target }}</p></body></html>"""
        elif report_type == 'technical':
            return """<!DOCTYPE html><html><head><title>Technical Report</title><style>{{ css }}</style></head><body><h1>Technical Report</h1><p>{{ target }}</p></body></html>"""
        else:
            return """<!DOCTYPE html><html><head><title>Report</title><style>{{ css }}</style></head><body><h1>Report</h1></body></html>"""
