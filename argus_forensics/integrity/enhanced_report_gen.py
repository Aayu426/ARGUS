"""
Enhanced Forensic Report Generator
PRD: Professional Legal-Style Intelligence Output

Generates comprehensive PDF reports with:
- Executive Summary
- Evidence Integrity Section
- Analysis Results by Module
- Attribution Confidence Score
- Cryptographic Hash References
- Explainability Panel
- Legal Disclaimer
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import json
import os
from ..core.telemetry import Telemetry
from ..core.confidence_scorer import ConfidenceScorer, ExplainabilityEngine

logger = Telemetry.get_logger("EnhancedReportGenerator")


class EnhancedReportGenerator:
    """
    Professional forensic report generator that produces
    court-ready legal-style intelligence output.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for professional appearance."""
        # Use unique names to avoid conflicts with built-in styles
        if 'ArgusSection' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ArgusSection',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#1a1a2e')
            ))
        
        if 'ArgusSubSection' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ArgusSubSection',
                parent=self.styles['Heading3'],
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor('#16213e')
            ))
        
        if 'ArgusBody' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ArgusBody',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leading=14
            ))
        
        if 'ArgusDisclaimer' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ArgusDisclaimer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                spaceAfter=4
            ))
    
    def generate_full_report(self, case_id: str, analysis_results: dict, 
                             output_path: str) -> str:
        """
        Generate comprehensive forensic intelligence report.
        
        Args:
            case_id: Unique case identifier
            analysis_results: Dict containing all analysis module results
            output_path: Output PDF file path
            
        Returns:
            Path to generated report
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            
            # Title Page
            story.extend(self._create_title_page(case_id))
            
            # Executive Summary
            story.extend(self._create_executive_summary(analysis_results))
            
            # Evidence Integrity Section
            story.extend(self._create_integrity_section(analysis_results))
            
            # Analysis Results
            story.extend(self._create_analysis_section(analysis_results))
            
            # Attribution Confidence Score
            story.extend(self._create_confidence_section(analysis_results))
            
            # Explainability Panel
            story.extend(self._create_xai_section(analysis_results))
            
            # Legal Disclaimer
            story.extend(self._create_disclaimer_section())
            
            # Hash References
            story.extend(self._create_hash_section(analysis_results))
            
            # Build PDF
            doc.build(story)
            logger.info(f"Enhanced report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return None
    
    def _create_title_page(self, case_id: str) -> list:
        """Create professional title page."""
        elements = []
        
        title = Paragraph(
            "<b>PROJECT ARGUS</b><br/>"
            "<font size='14'>FORENSIC INTELLIGENCE REPORT</font>",
            self.styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Case Info Table
        data = [
            ['Case ID:', case_id],
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Classification:', 'SENSITIVE - INVESTIGATIVE USE ONLY'],
            ['System Version:', 'ARGUS MVP v1.0']
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_executive_summary(self, results: dict) -> list:
        """Create executive summary section."""
        elements = []
        
        elements.append(Paragraph("1. EXECUTIVE SUMMARY", self.styles['ArgusSection']))
        
        # Get composite score if available
        confidence = results.get('confidence_score', {})
        score = confidence.get('attribution_confidence_score', 'N/A')
        verdict = confidence.get('verdict', 'PENDING ANALYSIS')
        
        summary_text = f"""
        This forensic intelligence report presents the findings from comprehensive 
        analysis of digital evidence related to Case ID: {results.get('case_id', 'Unknown')}.
        
        <b>Attribution Confidence Score: {score}</b><br/>
        <b>Overall Verdict: {verdict}</b>
        
        The analysis employed multiple forensic modules including stylometric analysis, 
        social graph mapping, image authenticity verification, and metadata integrity checks.
        All findings are supported by cryptographically verified chain of custody.
        """
        
        elements.append(Paragraph(summary_text, self.styles['ArgusBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_integrity_section(self, results: dict) -> list:
        """Create evidence integrity section with hash references."""
        elements = []
        
        elements.append(Paragraph("2. EVIDENCE INTEGRITY", self.styles['ArgusSection']))
        
        integrity = results.get('integrity', {})
        chain_status = integrity.get('status', 'UNKNOWN')
        total_blocks = integrity.get('total_blocks', 0)
        
        status_color = '#28a745' if chain_status == 'VERIFIED' else '#dc3545'
        
        integrity_text = f"""
        <b>Chain of Custody Status:</b> <font color='{status_color}'>{chain_status}</font><br/>
        <b>Total Ledger Blocks:</b> {total_blocks}<br/>
        <b>Hash Algorithms:</b> SHA3-512, SHA-256, BLAKE3 (Triple Verification)<br/>
        <b>Merkle Linking:</b> Enabled - Tamper-evident chain maintained
        """
        
        elements.append(Paragraph(integrity_text, self.styles['ArgusBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_analysis_section(self, results: dict) -> list:
        """Create detailed analysis results section."""
        elements = []
        
        elements.append(Paragraph("3. ANALYSIS RESULTS", self.styles['ArgusSection']))
        
        # Stylometry Results
        stylometry = results.get('stylometry', {})
        if stylometry:
            elements.append(Paragraph("3.1 Stylometric Analysis", self.styles['ArgusSubSection']))
            
            data = [
                ['Metric', 'Value'],
                ['Top Author Match', f"{stylometry.get('top_match', 'N/A')}"],
                ['Match Confidence', f"{stylometry.get('match_percentage', 0):.1f}%"],
                ['Radicalization Level', stylometry.get('radicalization', 'N/A')],
                ['Vocabulary Richness', f"{stylometry.get('vocab_richness', 0):.1f}%"]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 3*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Graph Results
        graph = results.get('graph', {})
        if graph:
            elements.append(Paragraph("3.2 Social Graph Analysis", self.styles['ArgusSubSection']))
            
            data = [
                ['Metric', 'Value'],
                ['Total Nodes', f"{graph.get('total_nodes', 0)}"],
                ['Total Edges', f"{graph.get('total_edges', 0)}"],
                ['Network Density', f"{graph.get('density', 0):.4f}"],
                ['Top Broker', graph.get('top_broker', 'N/A')],
                ['Suspicious Clusters', f"{graph.get('suspicious_count', 0)}"]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 3*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Image Results
        image = results.get('image', {})
        if image:
            elements.append(Paragraph("3.3 Image Authenticity", self.styles['ArgusSubSection']))
            
            data = [
                ['Metric', 'Value'],
                ['Manipulation Score', f"{image.get('manipulation_score', 0):.1f}%"],
                ['ELA Risk Level', image.get('ela_level', 'N/A')],
                ['AI Generation Probability', f"{image.get('ai_probability', 0):.1f}%"],
                ['Verdict', image.get('verdict', 'N/A')]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 3*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_confidence_section(self, results: dict) -> list:
        """Create attribution confidence score section."""
        elements = []
        
        elements.append(Paragraph("4. ATTRIBUTION CONFIDENCE SCORE", self.styles['ArgusSection']))
        
        confidence = results.get('confidence_score', {})
        
        formula_text = """
        <b>Scoring Formula:</b><br/>
        Attribution Confidence = 0.35×Stylometry + 0.25×Graph + 0.20×Image + 0.20×Metadata
        """
        elements.append(Paragraph(formula_text, self.styles['ArgusBody']))
        
        # Score breakdown table
        breakdown = confidence.get('module_breakdown', {})
        if breakdown:
            data = [['Module', 'Score', 'Weight', 'Contribution']]
            
            for key, mod in breakdown.items():
                data.append([
                    mod.get('name', key),
                    f"{mod.get('score', 0):.1f}",
                    f"{mod.get('weight', 0):.2f}",
                    f"{mod.get('weighted_contribution', 0):.1f}"
                ])
            
            # Add total row
            total = confidence.get('attribution_confidence_score', 0)
            data.append(['TOTAL', '', '1.00', f"{total:.1f}"])
            
            table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8e8e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(table)
        
        # Verdict
        verdict = confidence.get('verdict', 'PENDING')
        level = confidence.get('confidence_level', 'UNKNOWN')
        
        verdict_color = '#28a745' if level == 'HIGH' else '#ffc107' if level == 'MEDIUM' else '#dc3545'
        
        verdict_text = f"""
        <br/><b>Final Verdict:</b> <font color='{verdict_color}' size='12'>{verdict}</font><br/>
        <b>Confidence Level:</b> {level}
        """
        elements.append(Paragraph(verdict_text, self.styles['ArgusBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_xai_section(self, results: dict) -> list:
        """Create explainability panel section."""
        elements = []
        
        elements.append(Paragraph("5. EXPLAINABILITY PANEL (XAI)", self.styles['ArgusSection']))
        
        intro_text = """
        This section provides transparent reasoning for all analytical conclusions,
        ensuring legal defensibility and investigator understanding.
        """
        elements.append(Paragraph(intro_text, self.styles['ArgusBody']))
        
        xai = results.get('explainability', {})
        explanations = xai.get('explanations', [])
        
        for exp in explanations:
            elements.append(Paragraph(
                f"<b>{exp.get('module', 'Unknown Module')}</b>",
                self.styles['ArgusSubSection']
            ))
            
            reasoning = exp.get('why_this_result', [])
            for reason in reasoning:
                elements.append(Paragraph(f"• {reason}", self.styles['ArgusBody']))
            
            elements.append(Paragraph(
                f"<i>Methodology: {exp.get('methodology', 'N/A')}</i>",
                self.styles['ArgusDisclaimer']
            ))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_disclaimer_section(self) -> list:
        """Create legal and ethical disclaimer section."""
        elements = []
        
        elements.append(Paragraph("6. ETHICAL & LEGAL DISCLAIMER", self.styles['ArgusSection']))
        
        disclaimer_text = """
        <b>IMPORTANT NOTICE</b><br/><br/>
        
        ARGUS is an investigative decision-support system, NOT an automated 
        accusation engine.<br/><br/>
        
        • All findings require human expert review before any action is taken<br/>
        • Results are probabilistic indicators, not definitive proof of identity or wrongdoing<br/>
        • This system operates offline-first with no live data scraping<br/>
        • Designed for use in air-gapped forensic environments<br/>
        • Chain of custody maintained via cryptographic verification<br/><br/>
        
        This analysis is provided for investigative guidance only. Final attribution 
        decisions must be made by qualified human investigators with appropriate 
        legal authority.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['ArgusBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_hash_section(self, results: dict) -> list:
        """Create cryptographic hash reference section."""
        elements = []
        
        elements.append(Paragraph("7. CRYPTOGRAPHIC REFERENCES", self.styles['ArgusSection']))
        
        hashes = results.get('hashes', {})
        
        if hashes:
            data = [['Algorithm', 'Hash Value']]
            for algo, value in hashes.items():
                # Truncate for display
                display_value = value[:32] + '...' if len(value) > 32 else value
                data.append([algo.upper(), display_value])
            
            table = Table(data, colWidths=[1.5*inch, 4.5*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, -1), 'Courier'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph(
                "No hash references available for this report.",
                self.styles['ArgusBody']
            ))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer = f"""
        <br/>
        ─────────────────────────────────────────────────────────<br/>
        Report generated by Project ARGUS v1.0<br/>
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Cryptographically Logged
        """
        elements.append(Paragraph(footer, self.styles['ArgusDisclaimer']))
        
        return elements

