"""
OPERATOR DASHBOARD - Threat-centric security operations dashboard.
Designed for tactical decision-making, not corporate presentations.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict


def generate_operator_dashboard_html(data: Dict, output_dir: Path) -> str:
    """
    Generate threat-centric operator dashboard HTML.
    
    Args:
        data: Dashboard data dictionary
        output_dir: Output directory for report
        
    Returns:
        Path to generated dashboard file
    """
    findings = data.get('findings', [])
    findings_by_category = data.get('findings_by_category', {})
    detected_apps = data.get('detected_apps', [])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THREAT ASSESSMENT - {data.get('target', 'Unknown')}</title>
    <style>
{data.get('css', '')}
    </style>
</head>
<body>
    <!-- HEADER: Immediate Context -->
    <header class="threat-header">
        <div class="header-grid">
            <div class="header-primary">
                <h1 class="threat-title">THREAT ASSESSMENT</h1>
                <div class="target-info">
                    <span class="label">TARGET:</span>
                    <span class="value endpoint">{data.get('target', 'Unknown')}</span>
                </div>
            </div>
            <div class="header-meta">
                <div class="meta-item">
                    <span class="label">SESSION:</span>
                    <span class="value">{data.get('session_id', 'Unknown')}</span>
                </div>
                <div class="meta-item">
                    <span class="label">MODE:</span>
                    <span class="value mode-{data.get('attack_mode', 'AGGRESSIVE').lower()}">{data.get('attack_mode', 'AGGRESSIVE')}</span>
                </div>
                <div class="meta-item">
                    <span class="label">AUTHORIZED:</span>
                    <span class="value {'authorized-yes' if data.get('authorized') else 'authorized-no'}">{'YES' if data.get('authorized') else 'NO'}</span>
                </div>
                <div class="meta-item">
                    <span class="label">TIMESTAMP:</span>
                    <span class="value">{data.get('timestamp', 'Unknown')}</span>
                </div>
            </div>
        </div>
    </header>

    <!-- THREAT SUMMARY: Above the Fold -->
    <section class="threat-summary">
        <h2 class="section-title">THREAT SUMMARY</h2>
        <div class="summary-grid">
            <div class="summary-card exposure">
                <div class="card-header">
                    <span class="card-label">EXPOSURE SCORE</span>
                    <span class="card-value exposure-{_get_exposure_level(data.get('exposure_score', 0))}">{data.get('exposure_score', 0)}</span>
                </div>
                <div class="card-body">
                    <p class="exposure-note">Attack surface exposure metric. High score indicates larger attack surface regardless of detected vulnerabilities.</p>
                    <div class="exposure-breakdown">
                        <span>Endpoints: {data.get('endpoints_discovered', 0)}</span>
                        <span>Parameters: {data.get('parameters_tested', 0)}</span>
                        {f'<span class="app-warning">Known Vulnerable Apps: {len(detected_apps)}</span>' if detected_apps else ''}
                    </div>
                </div>
            </div>
            
            <div class="summary-card findings">
                <div class="card-header">
                    <span class="card-label">FINDINGS</span>
                    <span class="card-value">{data.get('total_findings', 0)}</span>
                </div>
                <div class="card-body">
                    <div class="confidence-breakdown">
                        <div class="confidence-item high">
                            <span class="confidence-label">HIGH:</span>
                            <span class="confidence-value">{data.get('high_confidence', 0)}</span>
                        </div>
                        <div class="confidence-item medium">
                            <span class="confidence-label">MEDIUM:</span>
                            <span class="confidence-value">{data.get('medium_confidence', 0)}</span>
                        </div>
                        <div class="confidence-item low">
                            <span class="confidence-label">LOW:</span>
                            <span class="confidence-value">{data.get('low_confidence', 0)}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="summary-card risk-statement">
                <div class="card-header">
                    <span class="card-label">RISK STATEMENT</span>
                </div>
                <div class="card-body">
                    {_generate_risk_statement(data)}
                </div>
            </div>
        </div>
    </section>

    <!-- DETECTED VULNERABLE APPS -->
    {_generate_detected_apps_section(detected_apps) if detected_apps else ''}

    <!-- FINDINGS SECTION: Aggressive Framing -->
    <section class="findings-section">
        <h2 class="section-title">FINDINGS</h2>
        {_generate_findings_section(findings, findings_by_category, data.get('total_findings', 0))}
    </section>

    <!-- OPERATOR INSIGHT PANEL -->
    <section class="operator-insight">
        <h2 class="section-title">OPERATOR INSIGHT</h2>
        <div class="insight-grid">
            {_generate_operator_insights(data)}
        </div>
    </section>

    <!-- TECHNICAL DETAIL: Collapsible -->
    <section class="technical-detail">
        <h2 class="section-title">TECHNICAL DETAIL</h2>
        <details class="tech-details">
            <summary class="tech-summary">Raw Assessment Data</summary>
            <pre class="tech-content">{_format_technical_data(data)}</pre>
        </details>
    </section>

</body>
</html>"""
    
    # Save dashboard
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"threat_dashboard_{data.get('session_id', 'unknown')}_{timestamp}.html"
    filepath = output_dir / filename
    filepath.write_text(html)
    
    return str(filepath)


def _get_exposure_level(score: int) -> str:
    """Get exposure level string."""
    if score >= 70:
        return "critical"
    elif score >= 40:
        return "high"
    elif score >= 20:
        return "medium"
    else:
        return "low"


def _generate_risk_statement(data: Dict) -> str:
    """Generate threat-oriented risk statement."""
    total_findings = data.get('total_findings', 0)
    exposure_score = data.get('exposure_score', 0)
    detected_apps = data.get('detected_apps', [])
    
    statements = []
    
    if total_findings == 0:
        statements.append("<p class='risk-warning'>No exploitable vectors observed under current observation window.</p>")
        statements.append("<p class='risk-note'>Risk does NOT imply absence of vulnerability. Limited observation scope may not reflect full attack surface.</p>")
    else:
        high_conf = data.get('high_confidence', 0)
        if high_conf > 0:
            statements.append(f"<p class='risk-critical'>{high_conf} high-confidence vulnerability signals detected. Immediate defensive review recommended.</p>")
        else:
            statements.append(f"<p class='risk-medium'>{total_findings} vulnerability signals detected. Requires defensive analysis.</p>")
    
    if exposure_score >= 70:
        statements.append("<p class='risk-high'>Large attack surface detected. Multiple entry points increase exploitation probability.</p>")
    elif exposure_score >= 40:
        statements.append("<p class='risk-medium'>Moderate attack surface. Multiple potential attack vectors present.</p>")
    
    if detected_apps:
        statements.append(f"<p class='risk-critical'>Known vulnerable application framework detected. Tailored exploitation vectors may exist.</p>")
    
    return "".join(statements)


def _generate_detected_apps_section(detected_apps: list) -> str:
    """Generate detected apps warning section."""
    html = """
    <section class="detected-apps">
        <h2 class="section-title critical">DETECTED VULNERABLE APPLICATIONS</h2>
        <div class="app-list">
"""
    for app in detected_apps:
        html += f"""
            <div class="app-item">
                <span class="app-name">{app.get('name', 'Unknown')}</span>
                <span class="app-confidence confidence-{app.get('confidence', 'low')}">{app.get('confidence', 'low').upper()}</span>
            </div>
"""
    html += """
        </div>
        <p class="app-warning-text">Known vulnerable application frameworks detected. Tailored exploitation payloads may be effective.</p>
    </section>
"""
    return html


def _generate_findings_section(findings: list, findings_by_category: dict, total: int) -> str:
    """Generate findings section with threat-oriented framing."""
    if total == 0:
        return """
        <div class="no-findings">
            <p class="no-findings-warning">No vulnerability signals detected in current observation window.</p>
            <p class="no-findings-note">This does NOT indicate security. Consider:</p>
            <ul class="no-findings-list">
                <li>WAF/IDS may be blocking detection signals</li>
                <li>Limited observation scope may miss attack vectors</li>
                <li>Manual testing may reveal additional vectors</li>
                <li>Different attack modes may yield different results</li>
            </ul>
        </div>
"""
    
    html = ""
    
    # Group by category
    for category, category_findings in findings_by_category.items():
        html += f"""
        <div class="category-section">
            <h3 class="category-title">{category.upper().replace('_', ' ')}</h3>
            <div class="findings-list">
"""
        for finding in category_findings:
            html += _generate_finding_card(finding)
        html += """
            </div>
        </div>
"""
    
    return html


def _generate_finding_card(finding: dict) -> str:
    """Generate individual finding card with threat context."""
    confidence = finding.get('confidence', 'low')
    category = finding.get('category', 'unknown')
    vulnerable = finding.get('vulnerable', False)
    
    # Determine signal type
    signal_type = _determine_signal_type(finding)
    kill_chain_stage = _determine_kill_chain_stage(finding)
    attacker_value = _determine_attacker_value(finding)
    defensive_implication = _get_defensive_implication(finding)
    
    html = f"""
        <div class="finding-card confidence-{confidence} {'vulnerable' if vulnerable else ''}">
            <div class="finding-header">
                <span class="severity-badge severity-{confidence}">{confidence.upper()}</span>
                <span class="signal-type">{signal_type}</span>
                <span class="kill-chain">{kill_chain_stage}</span>
            </div>
            <div class="finding-body">
                <div class="finding-endpoint">
                    <span class="label">ENDPOINT:</span>
                    <span class="value endpoint">{finding.get('endpoint', 'N/A')}</span>
                </div>
                <div class="finding-parameter">
                    <span class="label">PARAMETER:</span>
                    <span class="value parameter">{finding.get('parameter', 'N/A')}</span>
                </div>
                <div class="finding-method">
                    <span class="label">METHOD:</span>
                    <span class="value">{finding.get('method', 'N/A')}</span>
                </div>
                <div class="finding-payload">
                    <span class="label">PAYLOAD:</span>
                    <code class="payload-value">{finding.get('payload', 'N/A')}</code>
                </div>
                <div class="finding-evidence">
                    <span class="label">EVIDENCE:</span>
                    <ul class="evidence-list">
"""
    for evidence in finding.get('evidence', []):
        html += f"<li>{evidence}</li>\n"
    defensive_implication = _get_defensive_implication(finding)
    status_code = finding.get('status_code', 'N/A')
    response_time = finding.get('response_time', 0)
    response_snippet = finding.get('response_snippet', 'N/A')[:500]
    
    html += f"""
                    </ul>
                </div>
                <div class="finding-context">
                    <div class="context-item">
                        <span class="context-label">ATTACKER VALUE:</span>
                        <span class="context-value">{attacker_value}</span>
                    </div>
                    <div class="context-item">
                        <span class="context-label">DEFENSIVE IMPLICATION:</span>
                        <span class="context-value">{defensive_implication}</span>
                    </div>
                </div>
                <details class="finding-details">
                    <summary>Technical Details</summary>
                    <div class="technical-details">
                        <div class="detail-item">
                            <span class="detail-label">Status Code:</span>
                            <span class="detail-value">{status_code}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Response Time:</span>
                            <span class="detail-value">{response_time:.2f}s</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Response Snippet:</span>
                            <pre class="response-snippet">{response_snippet}</pre>
                        </div>
                    </div>
                </details>
            </div>
        </div>
"""
    return html


def _determine_signal_type(finding: dict) -> str:
    """Determine signal type for finding."""
    category = finding.get('category', '')
    if 'sql' in category.lower():
        return "BEHAVIORAL"
    elif 'xss' in category.lower():
        return "EXECUTION"
    elif 'command' in category.lower():
        return "EXECUTION"
    elif 'ssti' in category.lower():
        return "EXECUTION"
    elif 'lfi' in category.lower():
        return "EXPOSURE"
    elif 'auth' in category.lower():
        return "TRUST BOUNDARY"
    else:
        return "BEHAVIORAL"


def _determine_kill_chain_stage(finding: dict) -> str:
    """Determine kill chain stage."""
    category = finding.get('category', '')
    if 'auth' in category.lower() or 'bypass' in category.lower():
        return "INITIAL ACCESS"
    elif 'lfi' in category.lower() or 'command' in category.lower():
        return "EXECUTION"
    elif 'xss' in category.lower() or 'ssti' in category.lower():
        return "EXECUTION"
    elif 'sql' in category.lower():
        return "COLLECTION"
    else:
        return "RECONNAISSANCE"


def _determine_attacker_value(finding: dict) -> str:
    """Determine what kind of attacker would value this."""
    category = finding.get('category', '')
    confidence = finding.get('confidence', 'low')
    
    if confidence == 'high':
        if 'sql' in category.lower():
            return "Data exfiltration, privilege escalation"
        elif 'command' in category.lower() or 'ssti' in category.lower():
            return "System compromise, lateral movement"
        elif 'auth' in category.lower():
            return "Initial access, privilege escalation"
        else:
            return "Exploitation vector"
    else:
        return "Reconnaissance-grade intelligence"


def _get_defensive_implication(finding: dict) -> str:
    """Get defensive implication."""
    category = finding.get('category', '')
    if 'sql' in category.lower():
        return "Database access possible. Implement parameterized queries."
    elif 'xss' in category.lower():
        return "Client-side execution possible. Implement output encoding."
    elif 'command' in category.lower():
        return "System command execution possible. Implement input validation."
    elif 'ssti' in category.lower():
        return "Server-side code execution possible. Sanitize template inputs."
    elif 'lfi' in category.lower():
        return "File system access possible. Implement path validation."
    elif 'auth' in category.lower():
        return "Authentication bypass possible. Review auth logic."
    else:
        return "Security control review required."


def _generate_operator_insights(data: dict) -> str:
    """Generate operator insight panel."""
    findings = data.get('findings', [])
    total = len(findings)
    high_conf = data.get('high_confidence', 0)
    detected_apps = data.get('detected_apps', [])
    
    insights = []
    
    if high_conf > 0:
        insights.append("""
            <div class="insight-card critical">
                <h4>HIGH-CONFIDENCE SIGNALS</h4>
                <p>Multiple high-confidence vulnerability signals detected. These represent exploitable attack vectors requiring immediate defensive response.</p>
            </div>
        """)
    
    if detected_apps:
        insights.append(f"""
            <div class="insight-card high">
                <h4>KNOWN VULNERABLE FRAMEWORK</h4>
                <p>Target uses known vulnerable application framework. Tailored exploitation techniques may be effective. Standard security controls may be insufficient.</p>
            </div>
        """)
    
    if total == 0 and data.get('exposure_score', 0) > 40:
        insights.append("""
            <div class="insight-card medium">
                <h4>LARGE ATTACK SURFACE, NO SIGNALS</h4>
                <p>Significant attack surface detected but no vulnerability signals. This may indicate: WAF/IDS blocking, limited observation scope, or need for manual testing.</p>
            </div>
        """)
    
    if total > 0:
        insights.append(f"""
            <div class="insight-card info">
                <h4>ATTACK VECTOR ANALYSIS</h4>
                <p>{total} vulnerability signals across multiple categories. Attackers would prioritize high-confidence findings for exploitation. Medium/low confidence findings provide reconnaissance value.</p>
            </div>
        """)
    
    return "".join(insights) if insights else """
        <div class="insight-card info">
            <h4>OBSERVATION WINDOW</h4>
            <p>Limited observation scope. No vulnerability signals detected. Manual testing and expanded scope recommended for comprehensive assessment.</p>
        </div>
    """


def _format_technical_data(data: dict) -> str:
    """Format technical data as JSON."""
    import json
    # Remove css from technical data
    tech_data = {k: v for k, v in data.items() if k != 'css'}
    return json.dumps(tech_data, indent=2, default=str)
