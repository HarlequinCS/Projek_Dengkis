"""
Advanced security data visualization engine for PROJEK DENGKIS.
Transforms complex security assessment findings into interactive visualizations.
"""
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import io
import base64


class SecurityVisualizer:
    """
    Advanced security data visualization engine that transforms complex
    assessment findings into interactive, intuitive visual representations.
    Implements graph, timeline, geospatial, and statistical visualization
    techniques for comprehensive security analysis.
    """
    
    def __init__(self):
        self.color_palette = {
            'critical': '#FF4B4B',
            'high': '#FF8C42',
            'medium': '#FFD166',
            'low': '#06D6A0',
            'info': '#118AB2',
            'neutral': '#073B4C'
        }
        self.graph_layouts = {
            'hierarchical': 'dot',
            'circular': 'circo',
            'force_directed': 'fdp',
            'spring': 'neato'
        }
    
    def generate_attack_graph(self, findings: List[Dict], session: Dict) -> Dict:
        """
        Generate interactive attack graph visualization showing relationships
        between vulnerabilities, attack paths, and security controls.
        
        Args:
            findings: List of assessment findings
            session: Assessment session data
            
        Returns:
            Dict containing interactive graph data and configuration
        """
        G = nx.DiGraph()
        
        # Add nodes for findings
        for finding in findings:
            finding_id = finding.get('id', f"finding_{findings.index(finding)}")
            severity = finding.get('severity', 'info').lower()
            G.add_node(
                finding_id,
                label=finding.get('title', 'Unknown'),
                severity=severity,
                node_type='vulnerability',
                color=self.color_palette.get(severity, self.color_palette['info'])
            )
        
        # Add target node
        target = session.get('target', 'Unknown Target')
        G.add_node(
            'target',
            label=target,
            node_type='target',
            color=self.color_palette['neutral']
        )
        
        # Connect findings to target
        for finding in findings:
            finding_id = finding.get('id', f"finding_{findings.index(finding)}")
            G.add_edge(finding_id, 'target')
        
        # Create graph visualization using plotly
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Prepare edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            node_text.append(node_data.get('label', node))
            node_color.append(node_data.get('color', self.color_palette['info']))
            
            # Size based on severity
            severity = node_data.get('severity', 'info')
            size_map = {'critical': 20, 'high': 16, 'medium': 12, 'low': 10, 'info': 8}
            node_size.append(size_map.get(severity, 10))
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            hoverinfo='text',
            hovertext=node_text
        )
        
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Attack Graph Visualization',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        return {
            'type': 'attack_graph',
            'graph_data': fig.to_dict(),
            'node_count': len(G.nodes()),
            'edge_count': len(G.edges()),
            'html': fig.to_html(include_plotlyjs='cdn')
        }
    
    def create_timeline_visualization(self, events: List[Dict], time_range: str = 'auto') -> Dict:
        """
        Create interactive timeline visualization of security events,
        assessment activities, and potential attack progression.
        
        Args:
            events: List of security events with timestamps
            time_range: Time range for visualization ('auto', 'hour', 'day', 'week')
            
        Returns:
            Dict containing interactive timeline data and configuration
        """
        if not events:
            return {'type': 'timeline', 'error': 'No events provided'}
        
        # Convert events to DataFrame
        df = pd.DataFrame(events)
        
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(datetime.utcnow())
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add severity column with defaults
        if 'severity' not in df.columns:
            df['severity'] = 'info'
        
        # Create color mapping
        df['color'] = df['severity'].map(
            lambda x: self.color_palette.get(x.lower(), self.color_palette['info'])
        )
        
        # Create timeline figure
        fig = go.Figure()
        
        for severity in df['severity'].unique():
            severity_df = df[df['severity'] == severity]
            fig.add_trace(go.Scatter(
                x=severity_df['timestamp'],
                y=[severity] * len(severity_df),
                mode='markers+lines',
                name=severity.title(),
                marker=dict(
                    size=10,
                    color=self.color_palette.get(severity.lower(), self.color_palette['info'])
                ),
                text=severity_df.get('description', ''),
                hovertemplate='<b>%{text}</b><br>Time: %{x}<br>Severity: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Security Events Timeline',
            xaxis_title='Time',
            yaxis_title='Severity',
            hovermode='closest',
            plot_bgcolor='white',
            height=400
        )
        
        return {
            'type': 'timeline',
            'timeline_data': fig.to_dict(),
            'event_count': len(events),
            'html': fig.to_html(include_plotlyjs='cdn')
        }
    
    def generate_risk_heatmap(self, findings: List[Dict], dimensions: List[str]) -> Dict:
        """
        Generate risk heatmap showing vulnerability distribution across
        specified dimensions (e.g., systems, severity, exploitability).
        
        Args:
            findings: List of assessment findings
            dimensions: Dimensions for heatmap analysis
            
        Returns:
            Dict containing heatmap data and configuration
        """
        if not findings:
            return {'type': 'heatmap', 'error': 'No findings provided'}
        
        # Prepare data for heatmap
        df = pd.DataFrame(findings)
        
        # Default dimensions if not provided
        if not dimensions:
            dimensions = ['severity', 'category']
        
        # Create pivot table for heatmap
        heatmap_data = {}
        
        if 'severity' in df.columns and len(dimensions) > 1:
            pivot_dim = dimensions[1] if dimensions[1] in df.columns else 'category'
            heatmap_data = df.groupby(['severity', pivot_dim]).size().unstack(fill_value=0)
        else:
            # Simple count by first dimension
            if dimensions[0] in df.columns:
                heatmap_data = df[dimensions[0]].value_counts().to_dict()
            else:
                heatmap_data = {'Unknown': len(findings)}
        
        # Create heatmap
        if isinstance(heatmap_data, pd.DataFrame):
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns.tolist(),
                y=heatmap_data.index.tolist(),
                colorscale='RdYlGn_r',
                text=heatmap_data.values,
                texttemplate='%{text}',
                textfont={"size": 12},
                hoverongaps=False
            ))
        else:
            # Simple bar chart if not enough dimensions
            fig = go.Figure(data=go.Bar(
                x=list(heatmap_data.keys()),
                y=list(heatmap_data.values()),
                marker_color=self.color_palette['info']
            ))
        
        fig.update_layout(
            title='Risk Heatmap',
            xaxis_title=dimensions[-1] if len(dimensions) > 1 else 'Category',
            yaxis_title='Count',
            plot_bgcolor='white',
            height=400
        )
        
        return {
            'type': 'heatmap',
            'heatmap_data': fig.to_dict(),
            'dimensions': dimensions,
            'html': fig.to_html(include_plotlyjs='cdn')
        }
    
    def create_vulnerability_sunburst(self, findings: List[Dict]) -> Dict:
        """
        Create interactive sunburst chart showing hierarchical
        relationships between vulnerability categories.
        
        Args:
            findings: List of assessment findings
            
        Returns:
            Dict containing sunburst chart data and configuration
        """
        if not findings:
            return {'type': 'sunburst', 'error': 'No findings provided'}
        
        # Prepare hierarchical data
        df = pd.DataFrame(findings)
        
        # Build hierarchy: severity -> category -> finding
        hierarchy_data = []
        ids = []
        labels = []
        parents = []
        values = []
        
        # Group by severity and category
        if 'severity' in df.columns:
            for severity in df['severity'].unique():
                severity_id = f"severity_{severity}"
                ids.append(severity_id)
                labels.append(severity.title())
                parents.append("")
                values.append(len(df[df['severity'] == severity]))
                
                severity_df = df[df['severity'] == severity]
                if 'category' in severity_df.columns:
                    for category in severity_df['category'].unique():
                        category_id = f"{severity_id}_{category}"
                        ids.append(category_id)
                        labels.append(category)
                        parents.append(severity_id)
                        values.append(len(severity_df[severity_df['category'] == category]))
        
        if not ids:
            return {'type': 'sunburst', 'error': 'Insufficient data for sunburst'}
        
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colorscale='RdYlGn_r',
                line=dict(width=2)
            )
        ))
        
        fig.update_layout(
            title='Vulnerability Distribution Sunburst',
            height=500
        )
        
        return {
            'type': 'sunburst',
            'sunburst_data': fig.to_dict(),
            'html': fig.to_html(include_plotlyjs='cdn')
        }
    
    def generate_compliance_radar(self, compliance_data: Dict) -> Dict:
        """
        Generate radar chart showing compliance posture across
        multiple security frameworks and standards.
        
        Args:
            compliance_data: Compliance assessment data
            
        Returns:
            Dict containing radar chart data and configuration
        """
        if not compliance_data:
            return {'type': 'radar', 'error': 'No compliance data provided'}
        
        # Extract framework scores
        frameworks = compliance_data.get('frameworks', {})
        
        if not frameworks:
            return {'type': 'radar', 'error': 'No framework data available'}
        
        fig = go.Figure()
        
        for framework_name, scores in frameworks.items():
            if isinstance(scores, dict):
                categories = list(scores.keys())
                values = list(scores.values())
            elif isinstance(scores, (int, float)):
                categories = ['Overall']
                values = [scores]
            else:
                continue
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=framework_name
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title='Compliance Radar Chart',
            height=500
        )
        
        return {
            'type': 'radar',
            'radar_data': fig.to_dict(),
            'html': fig.to_html(include_plotlyjs='cdn')
        }
    
    def create_attack_surface_3d(self, surface_data: Dict) -> Dict:
        """
        Create 3D visualization of attack surface showing exposure
        across multiple dimensions.
        
        Args:
            surface_data: Attack surface analysis data
            
        Returns:
            Dict containing 3D visualization data and configuration
        """
        if not surface_data:
            return {'type': '3d_surface', 'error': 'No surface data provided'}
        
        # Extract dimensions
        entry_points = surface_data.get('entry_points', [])
        
        if not entry_points:
            return {'type': '3d_surface', 'error': 'No entry points data'}
        
        # Create 3D scatter plot
        x = [ep.get('exposure_level', 0) for ep in entry_points]
        y = [ep.get('complexity', 0) for ep in entry_points]
        z = [ep.get('risk_score', 0) for ep in entry_points]
        
        colors = [self.color_palette.get(ep.get('severity', 'info').lower(), self.color_palette['info']) 
                 for ep in entry_points]
        
        fig = go.Figure(data=[go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=10,
                color=colors,
                opacity=0.8
            ),
            text=[ep.get('type', 'Unknown') for ep in entry_points],
            hovertemplate='<b>%{text}</b><br>Exposure: %{x}<br>Complexity: %{y}<br>Risk: %{z}<extra></extra>'
        )])
        
        fig.update_layout(
            title='3D Attack Surface Visualization',
            scene=dict(
                xaxis_title='Exposure Level',
                yaxis_title='Complexity',
                zaxis_title='Risk Score'
            ),
            height=600
        )
        
        return {
            'type': '3d_surface',
            'surface_data': fig.to_dict(),
            'html': fig.to_html(include_plotlyjs='cdn')
        }
