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
    
    def generate_attack_report(self, assessment_data: Dict, format: str = 'html') -> str:
        """
        Generate ATTACKER-STYLE report with payloads, evidence, and exploitation details.
        This is NOT a compliance report - it's an attack report.
        
        Args:
            assessment_data: Complete attack results data
            format: Output format ('html', 'json', 'markdown')
            
        Returns:
            Path to generated attack report
        """
        findings = assessment_data.get('findings', [])
        attack_mode = assessment_data.get('attack_mode', 'aggressive')
        detected_apps = assessment_data.get('detected_apps', [])
        crawl_results = assessment_data.get('crawl_results', {})
        
        # Group findings by category
        findings_by_category = {}
        for finding in findings:
            category = finding.get('category', 'unknown')
            if category not in findings_by_category:
                findings_by_category[category] = []
            findings_by_category[category].append(finding)
        
        # Prepare attack data
        attack_data = {
            'target': assessment_data.get('target', 'Unknown'),
            'session_id': assessment_data.get('session_id', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'attack_mode': attack_mode.upper(),
            'total_findings': len(findings),
            'high_confidence': len([f for f in findings if f.get('confidence') == 'high']),
            'medium_confidence': len([f for f in findings if f.get('confidence') == 'medium']),
            'low_confidence': len([f for f in findings if f.get('confidence') == 'low']),
            'findings': findings,
            'findings_by_category': findings_by_category,
            'detected_apps': detected_apps,
            'endpoints_discovered': crawl_results.get('total_endpoints', 0),
            'parameters_tested': crawl_results.get('total_parameters', 0),
            'css': self._get_attack_css()
        }
        
        if format == 'html':
            return self._generate_attack_html_report(attack_data)
        elif format == 'json':
            return self._generate_json_report(attack_data, 'attack')
        elif format == 'markdown':
            return self._generate_attack_markdown_report(attack_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _get_attack_css(self) -> str:
        """Get CSS for attacker-style report."""
        return """
        body { font-family: 'Courier New', monospace; margin: 0; padding: 20px; background-color: #0a0a0a; color: #00ff00; }
        .header { background-color: #1a1a1a; color: #ff0000; padding: 20px; border: 2px solid #ff0000; margin-bottom: 20px; }
        .header h1 { color: #ff0000; text-shadow: 0 0 10px #ff0000; }
        .warning { color: #ffaa00; font-weight: bold; }
        .critical { color: #ff0000; font-weight: bold; }
        .high { color: #ff6600; font-weight: bold; }
        .medium { color: #ffaa00; font-weight: bold; }
        .low { color: #00ff00; font-weight: bold; }
        .finding { border: 1px solid #333; padding: 15px; margin: 15px 0; background-color: #1a1a1a; }
        .finding.vulnerable { border-left: 5px solid #ff0000; }
        .payload { background-color: #000; padding: 10px; border: 1px solid #333; font-family: monospace; color: #00ff00; margin: 10px 0; }
        .evidence { background-color: #1a1a1a; padding: 10px; border-left: 3px solid #ffaa00; margin: 10px 0; }
        .endpoint { color: #00aaff; font-family: monospace; }
        .parameter { color: #ff00ff; font-family: monospace; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; border: 1px solid #333; }
        th, td { border: 1px solid #333; padding: 12px; text-align: left; }
        th { background-color: #1a1a1a; color: #ff0000; }
        tr:nth-child(even) { background-color: #0f0f0f; }
        .summary { background-color: #1a1a1a; padding: 15px; border: 1px solid #333; margin: 20px 0; }
        .app-detected { background-color: #330000; padding: 10px; border: 2px solid #ff0000; margin: 10px 0; }
        """
    
    def _get_operator_dashboard_css(self) -> str:
        """Get CSS for threat-centric operator dashboard."""
        return """
        /* Base: Terminal meets cyber warfare */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            background-color: #0b0f14;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 0;
            margin: 0;
        }
        
        /* Typography */
        h1, h2, h3, h4 { font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.4em; margin-bottom: 1em; }
        h3 { font-size: 1.2em; }
        h4 { font-size: 1em; }
        
        /* Header: Immediate Context */
        .threat-header {
            background-color: #0b0f14;
            border-bottom: 2px solid #ff0000;
            padding: 1.5em 2em;
            margin-bottom: 2em;
        }
        .header-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2em;
        }
        .threat-title {
            color: #ff0000;
            font-size: 2em;
            margin-bottom: 0.5em;
            text-shadow: 0 0 10px #ff0000;
        }
        .target-info {
            display: flex;
            gap: 1em;
            align-items: center;
        }
        .label {
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .value {
            color: #e0e0e0;
            font-weight: 700;
        }
        .endpoint {
            color: #00aaff;
            font-family: monospace;
        }
        .parameter {
            color: #ff00ff;
            font-family: monospace;
        }
        .header-meta {
            display: flex;
            flex-direction: column;
            gap: 0.5em;
        }
        .meta-item {
            display: flex;
            gap: 0.5em;
        }
        .mode-aggressive { color: #ff6600; }
        .mode-active { color: #ffaa00; }
        .mode-passive { color: #00ff00; }
        .authorized-yes { color: #00ff00; }
        .authorized-no { color: #ff0000; }
        
        /* Threat Summary */
        .threat-summary {
            padding: 0 2em 2em;
        }
        .section-title {
            color: #ff0000;
            border-bottom: 1px solid #333;
            padding-bottom: 0.5em;
            margin-bottom: 1.5em;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5em;
        }
        .summary-card {
            background-color: #151920;
            border: 1px solid #333;
            padding: 1.5em;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #333;
        }
        .card-label {
            color: #888;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .card-value {
            font-size: 2em;
            font-weight: 700;
        }
        .exposure-critical { color: #ff0000; }
        .exposure-high { color: #ff6600; }
        .exposure-medium { color: #ffaa00; }
        .exposure-low { color: #00ff00; }
        .confidence-breakdown {
            display: flex;
            flex-direction: column;
            gap: 0.5em;
        }
        .confidence-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5em;
            background-color: #0b0f14;
        }
        .confidence-item.high .confidence-value { color: #ff6600; }
        .confidence-item.medium .confidence-value { color: #ffaa00; }
        .confidence-item.low .confidence-value { color: #00ff00; }
        .exposure-breakdown {
            display: flex;
            flex-direction: column;
            gap: 0.3em;
            font-size: 0.9em;
            color: #888;
        }
        .app-warning {
            color: #ff0000;
        }
        .risk-warning, .risk-critical, .risk-high, .risk-medium, .risk-note {
            margin: 0.5em 0;
            padding: 0.5em;
            background-color: #0b0f14;
        }
        .risk-critical { color: #ff0000; border-left: 3px solid #ff0000; }
        .risk-high { color: #ff6600; border-left: 3px solid #ff6600; }
        .risk-medium { color: #ffaa00; border-left: 3px solid #ffaa00; }
        .risk-warning { color: #ffaa00; }
        .risk-note { color: #888; font-size: 0.9em; }
        
        /* Detected Apps */
        .detected-apps {
            padding: 0 2em 2em;
            background-color: #1a0000;
            border: 2px solid #ff0000;
            margin: 2em;
        }
        .app-list {
            display: flex;
            flex-direction: column;
            gap: 0.5em;
            margin: 1em 0;
        }
        .app-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5em;
            background-color: #0b0f14;
        }
        .app-name {
            color: #ff0000;
            font-weight: 700;
        }
        .app-warning-text {
            color: #ff6600;
            margin-top: 1em;
        }
        
        /* Findings Section */
        .findings-section {
            padding: 0 2em 2em;
        }
        .category-section {
            margin-bottom: 2em;
        }
        .category-title {
            color: #ff6600;
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #333;
        }
        .findings-list {
            display: flex;
            flex-direction: column;
            gap: 1em;
        }
        .finding-card {
            background-color: #151920;
            border: 1px solid #333;
            padding: 1.5em;
        }
        .finding-card.vulnerable {
            border-left: 5px solid #ff0000;
        }
        .finding-header {
            display: flex;
            gap: 1em;
            align-items: center;
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #333;
        }
        .severity-badge {
            padding: 0.3em 0.8em;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .severity-high { background-color: #ff6600; color: #0b0f14; }
        .severity-medium { background-color: #ffaa00; color: #0b0f14; }
        .severity-low { background-color: #00ff00; color: #0b0f14; }
        .signal-type {
            color: #888;
            font-size: 0.9em;
        }
        .kill-chain {
            color: #00aaff;
            font-size: 0.9em;
        }
        .finding-body {
            display: flex;
            flex-direction: column;
            gap: 0.8em;
        }
        .finding-endpoint, .finding-parameter, .finding-method {
            display: flex;
            gap: 0.5em;
        }
        .finding-payload {
            background-color: #0b0f14;
            padding: 0.8em;
            border: 1px solid #333;
        }
        .payload-value {
            color: #00ff00;
            font-family: monospace;
        }
        .evidence-list {
            margin-left: 1.5em;
            color: #ffaa00;
        }
        .finding-context {
            margin-top: 1em;
            padding-top: 1em;
            border-top: 1px solid #333;
        }
        .context-item {
            display: flex;
            gap: 0.5em;
            margin: 0.5em 0;
        }
        .context-label {
            color: #888;
            font-size: 0.9em;
        }
        .context-value {
            color: #e0e0e0;
        }
        .finding-details {
            margin-top: 1em;
        }
        .tech-summary {
            color: #00aaff;
            cursor: pointer;
            padding: 0.5em;
            background-color: #0b0f14;
        }
        .technical-details {
            padding: 1em;
            background-color: #0b0f14;
            margin-top: 0.5em;
        }
        .detail-item {
            display: flex;
            gap: 0.5em;
            margin: 0.5em 0;
        }
        .response-snippet {
            background-color: #000;
            padding: 1em;
            overflow-x: auto;
            font-size: 0.85em;
            color: #888;
        }
        .no-findings {
            padding: 2em;
            background-color: #151920;
            border: 1px solid #333;
        }
        .no-findings-warning {
            color: #ffaa00;
            font-size: 1.1em;
            margin-bottom: 1em;
        }
        .no-findings-note {
            color: #888;
            margin: 1em 0;
        }
        .no-findings-list {
            margin-left: 1.5em;
            color: #888;
        }
        
        /* Operator Insight */
        .operator-insight {
            padding: 0 2em 2em;
        }
        .insight-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5em;
        }
        .insight-card {
            background-color: #151920;
            border: 1px solid #333;
            padding: 1.5em;
        }
        .insight-card.critical { border-left: 5px solid #ff0000; }
        .insight-card.high { border-left: 5px solid #ff6600; }
        .insight-card.medium { border-left: 5px solid #ffaa00; }
        .insight-card.info { border-left: 5px solid #00aaff; }
        .insight-card h4 {
            color: #ff0000;
            margin-bottom: 0.8em;
        }
        
        /* Technical Detail */
        .technical-detail {
            padding: 0 2em 2em;
        }
        .tech-details {
            background-color: #151920;
            border: 1px solid #333;
        }
        .tech-content {
            padding: 1em;
            background-color: #0b0f14;
            overflow-x: auto;
            font-size: 0.85em;
            color: #888;
        }
        """
    
    def _generate_operator_dashboard(self, dashboard_data: Dict) -> str:
        """Generate operator dashboard using dedicated module."""
        from engine.reporting.operator_dashboard import generate_operator_dashboard_html
        return generate_operator_dashboard_html(dashboard_data, self.output_dir)
    
    def _generate_attack_html_report(self, attack_data: Dict) -> str:
        """Generate HTML attack report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ATTACK REPORT - {attack_data['target']}</title>
    <style>{attack_data['css']}</style>
</head>
<body>
    <div class="header">
        <h1>⚠ ATTACK REPORT ⚠</h1>
        <p><strong>Target:</strong> {attack_data['target']}</p>
        <p><strong>Attack Mode:</strong> {attack_data['attack_mode']}</p>
        <p><strong>Session ID:</strong> {attack_data['session_id']}</p>
        <p><strong>Generated:</strong> {attack_data['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>ATTACK SUMMARY</h2>
        <p><strong>Total Findings:</strong> <span class="critical">{attack_data['total_findings']}</span></p>
        <p><strong>High Confidence:</strong> <span class="high">{attack_data['high_confidence']}</span></p>
        <p><strong>Medium Confidence:</strong> <span class="medium">{attack_data['medium_confidence']}</span></p>
        <p><strong>Low Confidence:</strong> <span class="low">{attack_data['low_confidence']}</span></p>
        <p><strong>Endpoints Discovered:</strong> {attack_data['endpoints_discovered']}</p>
        <p><strong>Parameters Tested:</strong> {attack_data['parameters_tested']}</p>
    </div>
"""
        
        # Detected apps
        if attack_data['detected_apps']:
            html += """
    <div class="app-detected">
        <h2>⚠ DETECTED VULNERABLE APPS ⚠</h2>
"""
            for app in attack_data['detected_apps']:
                html += f"""
        <p><strong>{app['name']}</strong> (confidence: {app['confidence']})</p>
"""
            html += """
    </div>
"""
        
        # Findings by category
        html += """
    <h2>FINDINGS BY CATEGORY</h2>
"""
        for category, findings in attack_data['findings_by_category'].items():
            html += f"""
    <h3>{category.upper().replace('_', ' ')} ({len(findings)} findings)</h3>
"""
            for finding in findings:
                vulnerable = finding.get('vulnerable', False)
                confidence = finding.get('confidence', 'low')
                html += f"""
    <div class="finding {'vulnerable' if vulnerable else ''}">
        <h4>Endpoint: <span class="endpoint">{finding.get('endpoint', 'N/A')}</span></h4>
        <p><strong>Parameter:</strong> <span class="parameter">{finding.get('parameter', 'N/A')}</span></p>
        <p><strong>Method:</strong> {finding.get('method', 'N/A')}</p>
        <p><strong>Vulnerable:</strong> <span class="{'critical' if vulnerable else 'low'}">{'YES' if vulnerable else 'NO'}</span></p>
        <p><strong>Confidence:</strong> <span class="{confidence}">{confidence.upper()}</span></p>
        <p><strong>Category:</strong> {finding.get('category', 'N/A')}</p>
        <p><strong>Type:</strong> {finding.get('type', 'N/A')}</p>
        
        <div class="payload">
            <strong>PAYLOAD USED:</strong><br>
            {finding.get('payload', 'N/A')}
        </div>
        
        <div class="evidence">
            <strong>EVIDENCE:</strong><br>
            <ul>
"""
                for evidence_item in finding.get('evidence', []):
                    html += f"<li>{evidence_item}</li>\n"
                html += """
            </ul>
        </div>
        
        <p><strong>Status Code:</strong> {finding.get('status_code', 'N/A')}</p>
        <p><strong>Response Time:</strong> {finding.get('response_time', 0):.2f}s</p>
        
        <details>
            <summary>Response Snippet</summary>
            <pre style="background: #000; padding: 10px; overflow-x: auto;">{finding.get('response_snippet', 'N/A')[:500]}</pre>
        </details>
        
        <details>
            <summary>Baseline Comparison</summary>
            <pre style="background: #000; padding: 10px;">{json.dumps(finding.get('baseline_comparison', {}), indent=2)}</pre>
        </details>
    </div>
"""
        
        # If no findings
        if attack_data['total_findings'] == 0:
            html += """
    <div class="finding">
        <h3>⚠ NO FINDINGS DETECTED ⚠</h3>
        <p>No vulnerabilities were automatically detected. This could mean:</p>
        <ul>
            <li>The target is well-secured (unlikely)</li>
            <li>WAF/IDS is blocking payloads</li>
            <li>Manual testing required</li>
            <li>Different attack vectors needed</li>
        </ul>
"""
            if attack_data['detected_apps']:
                html += """
        <p class="warning"><strong>WARNING:</strong> Known vulnerable app detected but 0 findings! Manual testing REQUIRED.</p>
"""
            html += """
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"attack_report_{attack_data['session_id']}_{timestamp}.html"
        report_path = self.output_dir / filename
        report_path.write_text(html)
        
        return str(report_path)
    
    def _generate_attack_markdown_report(self, attack_data: Dict) -> str:
        """Generate Markdown attack report."""
        md = f"""# ATTACK REPORT

**Target:** {attack_data['target']}  
**Attack Mode:** {attack_data['attack_mode']}  
**Session ID:** {attack_data['session_id']}  
**Generated:** {attack_data['timestamp']}

## ATTACK SUMMARY

- **Total Findings:** {attack_data['total_findings']}
- **High Confidence:** {attack_data['high_confidence']}
- **Medium Confidence:** {attack_data['medium_confidence']}
- **Low Confidence:** {attack_data['low_confidence']}
- **Endpoints Discovered:** {attack_data['endpoints_discovered']}
- **Parameters Tested:** {attack_data['parameters_tested']}

"""
        
        # Detected apps
        if attack_data['detected_apps']:
            md += "## DETECTED VULNERABLE APPS\n\n"
            for app in attack_data['detected_apps']:
                md += f"- **{app['name']}** (confidence: {app['confidence']})\n"
            md += "\n"
        
        # Findings
        md += "## FINDINGS\n\n"
        for finding in attack_data['findings']:
            md += f"""### {finding.get('category', 'unknown').upper().replace('_', ' ')}

- **Endpoint:** `{finding.get('endpoint', 'N/A')}`
- **Parameter:** `{finding.get('parameter', 'N/A')}`
- **Method:** {finding.get('method', 'N/A')}
- **Vulnerable:** {'YES' if finding.get('vulnerable') else 'NO'}
- **Confidence:** {finding.get('confidence', 'low').upper()}
- **Payload:** `{finding.get('payload', 'N/A')}`

**Evidence:**
"""
            for evidence_item in finding.get('evidence', []):
                md += f"- {evidence_item}\n"
            md += "\n"
        
        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"attack_report_{attack_data['session_id']}_{timestamp}.md"
        report_path = self.output_dir / filename
        report_path.write_text(md)
        
        return str(report_path)
    
    def create_interactive_dashboard(self, assessment_data: Dict) -> str:
        """
        Create threat-centric operator dashboard with tactical insights.
        Designed for security operations, not marketing.
        
        Args:
            assessment_data: Complete assessment data
            
        Returns:
            Path to generated dashboard file
        """
        findings = assessment_data.get('findings', [])
        attack_mode = assessment_data.get('attack_mode', 'aggressive')
        detected_apps = assessment_data.get('detected_apps', [])
        crawl_results = assessment_data.get('crawl_results', {})
        
        # Calculate threat metrics
        high_confidence = len([f for f in findings if f.get('confidence') == 'high'])
        medium_confidence = len([f for f in findings if f.get('confidence') == 'medium'])
        low_confidence = len([f for f in findings if f.get('confidence') == 'low'])
        
        # Group findings by category for operator analysis
        findings_by_category = {}
        for finding in findings:
            category = finding.get('category', 'unknown')
            if category not in findings_by_category:
                findings_by_category[category] = []
            findings_by_category[category].append(finding)
        
        # Calculate attack surface metrics
        endpoints_discovered = crawl_results.get('total_endpoints', 0)
        parameters_tested = crawl_results.get('total_parameters', 0)
        
        # Risk exposure score (derived from attack surface, not exploit-based)
        # Even with 0 findings, large attack surface = higher exposure
        exposure_score = min(100, (endpoints_discovered * 2) + (parameters_tested * 1))
        if detected_apps:
            exposure_score = min(100, exposure_score + 30)  # Known vulnerable apps increase exposure
        
        dashboard_data = {
            'target': assessment_data.get('target', 'Unknown'),
            'session_id': assessment_data.get('session_id', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'attack_mode': attack_mode.upper(),
            'authorized': assessment_data.get('authorized', False),
            'total_findings': len(findings),
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence,
            'findings': findings,
            'findings_by_category': findings_by_category,
            'detected_apps': detected_apps,
            'endpoints_discovered': endpoints_discovered,
            'parameters_tested': parameters_tested,
            'exposure_score': exposure_score,
            'css': self._get_operator_dashboard_css()
        }
        
        return self._generate_operator_dashboard(dashboard_data)
    
    def _generate_html_report(self, template_name: str, data: Dict, report_type: str) -> str:
        """Generate HTML report from template."""
        try:
            template = self.env.get_template(template_name)
        except:
            # Fallback to inline template
            template = Template(self._get_default_template(report_type))
        
        # Fix duplicate css argument: only add if not already in data
        render_data = data.copy()
        if 'css' not in render_data:
            render_data['css'] = self.custom_css
        
        html_content = template.render(**render_data)
        
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
