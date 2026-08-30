"""
Unified Case State and Evidence Processing Pipeline
Central hub for all case data, shared across all analysis modules.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("UnifiedPipeline")


@dataclass
class EntityInfo:
    """Represents an extracted entity."""
    name: str
    type: str  # PERSON, ORGANIZATION, LOCATION, etc.
    source: str  # Which file it came from
    context: str = ""  # Surrounding text
    risk_level: str = "UNKNOWN"  # LOW, MEDIUM, HIGH
    color: str = "#6b7280"  # Gray default


@dataclass 
class LocationData:
    """Represents geolocation data from an image."""
    address: str
    latitude: float
    longitude: float
    timestamp: Optional[str] = None
    source_file: str = ""
    map_url: str = ""


@dataclass
class ImageAnalysis:
    """Represents analysis results for an image."""
    file_path: str
    file_name: str
    gan_probability: float = 0.0
    ela_risk: str = "UNKNOWN"
    is_authentic: bool = True
    geotag: Optional[LocationData] = None
    device_info: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class TextAnalysis:
    """Represents NLP analysis results for text."""
    source_file: str
    text_preview: str
    language: str = "en"
    entities: List[EntityInfo] = field(default_factory=list)
    threat_score: float = 0.0
    stylometry_match: Optional[str] = None
    stylometry_score: float = 0.0
    key_phrases: List[str] = field(default_factory=list)


@dataclass
class Scenario:
    """Represents a generated scenario linking entity to location/time."""
    entity: str
    entity_type: str
    location: str
    coordinates: Optional[tuple] = None
    timestamp: Optional[str] = None
    evidence_source: str = ""
    description: str = ""
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    color: str = "#22c55e"  # Green default


@dataclass
class FinalAttribution:
    """Final suspect attribution with confidence."""
    suspect: str
    aliases: List[str] = field(default_factory=list)
    probable_location: str = ""
    role: str = ""
    confidence_score: float = 0.0
    evidence_summary: str = ""
    risk_breakdown: Dict = field(default_factory=dict)


@dataclass
class UnifiedCaseState:
    """
    Central state container for an entire case.
    All modules read/write to this shared state.
    """
    case_id: str
    created_at: str = ""
    status: str = "INITIALIZED"
    
    # Evidence files
    evidence_files: List[Dict] = field(default_factory=list)
    
    # Extracted data
    entities: List[EntityInfo] = field(default_factory=list)
    locations: List[LocationData] = field(default_factory=list)
    
    # Analysis results
    text_analyses: List[TextAnalysis] = field(default_factory=list)
    image_analyses: List[ImageAnalysis] = field(default_factory=list)
    
    # Graph data
    graph_nodes: List[Dict] = field(default_factory=list)
    graph_edges: List[Dict] = field(default_factory=list)
    graph_metrics: Dict = field(default_factory=dict)
    
    # Scenarios and attribution
    scenarios: List[Scenario] = field(default_factory=list)
    final_attribution: Optional[FinalAttribution] = None
    overall_risk_score: float = 0.0
    
    # Integrity
    evidence_hashes: Dict[str, str] = field(default_factory=dict)
    merkle_root: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        result = asdict(self)
        # Convert dataclass lists to dicts
        result["entities"] = [asdict(e) if hasattr(e, '__dataclass_fields__') else e for e in self.entities]
        result["scenarios"] = [asdict(s) if hasattr(s, '__dataclass_fields__') else s for s in self.scenarios]
        if self.final_attribution:
            result["final_attribution"] = asdict(self.final_attribution)
        return result


# Global in-memory case store
CASE_STORE: Dict[str, UnifiedCaseState] = {}


def get_case_state(case_id: str) -> UnifiedCaseState:
    """Get or create case state."""
    if case_id not in CASE_STORE:
        CASE_STORE[case_id] = UnifiedCaseState(case_id=case_id)
    return CASE_STORE[case_id]


def update_case_state(case_id: str, state: UnifiedCaseState):
    """Update case state in store."""
    CASE_STORE[case_id] = state


class EvidenceProcessor:
    """
    Processes all evidence in vault and populates unified case state.
    """
    
    def __init__(self, case_id: str, evidence_dir: str = "evidence_vault"):
        self.case_id = case_id
        self.evidence_dir = evidence_dir
        self.state = get_case_state(case_id)
        
    def process_all(self) -> UnifiedCaseState:
        """
        Main entry point: process all evidence files.
        Returns updated case state.
        """
        logger.info(f"Starting full evidence processing for case {self.case_id}")
        self.state.status = "PROCESSING"
        
        try:
            # Step 1: Scan and categorize files
            self._scan_evidence_files()
            
            # Step 2: Process text files (+ OCR for PDFs)
            self._process_text_files()
            
            # Step 3: Process images (authenticity + geotag)
            self._process_image_files()
            
            # Step 4: Build graph from entities
            self._build_entity_graph()
            
            # Step 5: Generate scenarios
            self._generate_scenarios()
            
            # Step 6: Calculate final attribution
            self._calculate_final_attribution()
            
            self.state.status = "COMPLETED"
            update_case_state(self.case_id, self.state)
            
            logger.info(f"Evidence processing complete. Found {len(self.state.entities)} entities, {len(self.state.scenarios)} scenarios")
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.state.status = f"ERROR: {str(e)}"
            
        return self.state
    
    def _scan_evidence_files(self):
        """Scan evidence directory and categorize files."""
        if not os.path.exists(self.evidence_dir):
            logger.warning(f"Evidence directory not found: {self.evidence_dir}")
            return
            
        for filename in os.listdir(self.evidence_dir):
            filepath = os.path.join(self.evidence_dir, filename)
            if not os.path.isfile(filepath):
                continue
                
            ext = filename.lower().split('.')[-1]
            file_type = self._get_file_type(ext)
            
            self.state.evidence_files.append({
                "name": filename,
                "path": filepath,
                "type": file_type,
                "extension": ext,
                "size": os.path.getsize(filepath),
                "processed": False
            })
            
        logger.info(f"Found {len(self.state.evidence_files)} evidence files")
    
    def _get_file_type(self, ext: str) -> str:
        """Categorize file by extension."""
        image_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']
        text_exts = ['txt', 'md', 'json', 'csv', 'log']
        doc_exts = ['pdf', 'doc', 'docx']
        
        if ext in image_exts:
            return "IMAGE"
        elif ext in text_exts:
            return "TEXT"
        elif ext in doc_exts:
            return "DOCUMENT"
        else:
            return "UNKNOWN"
    
    def _process_text_files(self):
        """Process all text files with NLP."""
        from ..nlp.stylometry import EnhancedStylometry
        
        for file_info in self.state.evidence_files:
            if file_info["type"] not in ["TEXT", "DOCUMENT"]:
                continue
                
            filepath = file_info["path"]
            text = self._extract_text(filepath, file_info["extension"])
            
            if not text or len(text.strip()) < 10:
                continue
            
            # Run NLP analysis
            analysis = self._analyze_text(text, file_info["name"])
            self.state.text_analyses.append(analysis)
            
            # Add entities to global list
            for entity in analysis.entities:
                if entity not in self.state.entities:
                    self.state.entities.append(entity)
            
            file_info["processed"] = True
            
        logger.info(f"Processed {len(self.state.text_analyses)} text files")
    
    def _extract_text(self, filepath: str, ext: str) -> str:
        """Extract text from file, using OCR for PDFs if needed."""
        try:
            if ext in ['txt', 'md', 'log']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
            elif ext == 'json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
                    
            elif ext == 'pdf':
                return self._extract_pdf_text(filepath)
                
            elif ext in ['doc', 'docx']:
                return self._extract_docx_text(filepath)
                
        except Exception as e:
            logger.error(f"Text extraction failed for {filepath}: {e}")
            
        return ""
    
    def _extract_pdf_text(self, filepath: str) -> str:
        """Extract text from PDF using PyMuPDF or OCR fallback."""
        text = ""
        
        # Try PyMuPDF first
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
            
            if text.strip():
                logger.info(f"Extracted {len(text)} chars from PDF via PyMuPDF")
                return text
        except ImportError:
            logger.warning("PyMuPDF not installed, trying OCR")
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")
        
        # OCR fallback with pytesseract
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(filepath)
            for img in images:
                text += pytesseract.image_to_string(img)
            
            logger.info(f"Extracted {len(text)} chars from PDF via OCR")
            return text
        except ImportError:
            logger.warning("pdf2image/pytesseract not installed")
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            
        return text
    
    def _extract_docx_text(self, filepath: str) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            logger.warning("python-docx not installed")
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
        return ""
    
    def _analyze_text(self, text: str, source_file: str) -> TextAnalysis:
        """Run NLP analysis on text."""
        import spacy
        
        analysis = TextAnalysis(
            source_file=source_file,
            text_preview=text[:500] + "..." if len(text) > 500 else text
        )
        
        # Load spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            try:
                nlp = spacy.load("xx_ent_wiki_sm")
            except:
                logger.error("No spaCy model available")
                return analysis
        
        doc = nlp(text[:10000])  # Limit for performance
        
        # Extract entities
        for ent in doc.ents:
            entity = EntityInfo(
                name=ent.text,
                type=ent.label_,
                source=source_file,
                context=text[max(0, ent.start_char-50):ent.end_char+50]
            )
            analysis.entities.append(entity)
        
        # Extract key phrases (nouns)
        analysis.key_phrases = list(set([
            chunk.text for chunk in doc.noun_chunks 
            if len(chunk.text) > 3
        ]))[:20]
        
        # Calculate threat score based on keywords
        threat_keywords = ['hack', 'attack', 'steal', 'fake', 'impersonate', 'credential', 
                          'breach', 'leak', 'compromise', 'malicious', 'fraud', 'scam']
        threat_count = sum(1 for kw in threat_keywords if kw in text.lower())
        analysis.threat_score = min(threat_count * 10, 100)
        
        return analysis
    
    def _process_image_files(self):
        """Process all images for authenticity and geotag."""
        from ..vision.gan_detector import GANDetector
        from ..vision.ela_analyzer import ELAAnalyzer
        from ..vision.geo_extractor import GeoExtractor
        
        gan_detector = GANDetector()
        ela_analyzer = ELAAnalyzer()
        geo_extractor = GeoExtractor()
        
        for file_info in self.state.evidence_files:
            if file_info["type"] != "IMAGE":
                continue
                
            filepath = file_info["path"]
            
            analysis = ImageAnalysis(
                file_path=filepath,
                file_name=file_info["name"]
            )
            
            try:
                # GAN detection
                gan_result = gan_detector.detect(filepath)
                analysis.gan_probability = gan_result.get("gan_probability", 0)
                analysis.is_authentic = analysis.gan_probability < 50
                
                # ELA analysis
                ela_result = ela_analyzer.full_analysis(filepath)
                analysis.ela_risk = ela_result.get("risk", {}).get("level", "UNKNOWN")
                
                # Geotag extraction
                geo_result = geo_extractor.extract_geotag(filepath)
                if geo_result.get("has_geotag"):
                    location = LocationData(
                        address=f"Lat {geo_result['latitude']}, Long {geo_result['longitude']}",
                        latitude=geo_result['latitude'],
                        longitude=geo_result['longitude'],
                        timestamp=geo_result.get('timestamp'),
                        source_file=file_info["name"],
                        map_url=geo_result.get('map_url', '')
                    )
                    analysis.geotag = location
                    analysis.device_info = geo_result.get('device_info', {})
                    self.state.locations.append(location)
                
                # Generate warnings
                if analysis.gan_probability > 70:
                    analysis.warnings.append("HIGH GAN probability - likely AI-generated")
                elif analysis.gan_probability > 40:
                    analysis.warnings.append("Moderate GAN indicators detected")
                    
                if analysis.ela_risk == "HIGH":
                    analysis.warnings.append("ELA shows significant manipulation")
                    
            except Exception as e:
                logger.error(f"Image analysis failed for {filepath}: {e}")
                analysis.warnings.append(f"Analysis error: {str(e)}")
            
            self.state.image_analyses.append(analysis)
            file_info["processed"] = True
            
        logger.info(f"Processed {len(self.state.image_analyses)} images")
    
    def _build_entity_graph(self):
        """Build graph from extracted entities and relationships."""
        from ..graph.hidden_nexus import EnhancedGraphAnalyzer
        
        # Create nodes from entities
        seen_nodes = set()
        for entity in self.state.entities:
            node_id = entity.name.lower().replace(" ", "_")
            if node_id not in seen_nodes:
                self.state.graph_nodes.append({
                    "id": node_id,
                    "label": entity.name,
                    "type": entity.type,
                    "risk": entity.risk_level
                })
                seen_nodes.add(node_id)
        
        # Create edges based on co-occurrence
        for i, e1 in enumerate(self.state.entities):
            for e2 in self.state.entities[i+1:]:
                if e1.source == e2.source:  # Same document = connection
                    self.state.graph_edges.append({
                        "from": e1.name.lower().replace(" ", "_"),
                        "to": e2.name.lower().replace(" ", "_"),
                        "type": "co_occurrence",
                        "weight": 1.0
                    })
        
        # Analyze graph
        if self.state.graph_edges:
            try:
                analyzer = EnhancedGraphAnalyzer()
                for edge in self.state.graph_edges:
                    analyzer.add_interaction(edge["from"], edge["to"], edge["type"])
                
                metrics = analyzer.analyze()
                self.state.graph_metrics = metrics
            except Exception as e:
                logger.error(f"Graph analysis failed: {e}")
        
        logger.info(f"Built graph with {len(self.state.graph_nodes)} nodes, {len(self.state.graph_edges)} edges")
    
    def _generate_scenarios(self):
        """Generate scenarios linking entities to locations and times."""
        
        # Link entities to locations
        for location in self.state.locations:
            for entity in self.state.entities:
                if entity.type == "PERSON":
                    scenario = Scenario(
                        entity=entity.name,
                        entity_type="PERSON",
                        location=location.address,
                        coordinates=(location.latitude, location.longitude),
                        timestamp=location.timestamp,
                        evidence_source=location.source_file,
                        description=f"{entity.name} potentially connected to location in {location.address}",
                        risk_level="MEDIUM"
                    )
                    
                    # Adjust risk based on context
                    if "suspect" in entity.name.lower() or entity.risk_level == "HIGH":
                        scenario.risk_level = "HIGH"
                        scenario.color = "#ef4444"  # Red
                        scenario.description = f"SUSPECT {entity.name} at {location.address} on {location.timestamp or 'unknown date'}"
                    elif "victim" in entity.context.lower():
                        scenario.risk_level = "LOW"
                        scenario.color = "#22c55e"  # Green
                    else:
                        scenario.color = "#f59e0b"  # Amber
                    
                    self.state.scenarios.append(scenario)
        
        # Create scenarios from image analysis
        for img in self.state.image_analyses:
            if not img.is_authentic:
                scenario = Scenario(
                    entity=img.file_name,
                    entity_type="EVIDENCE",
                    location="Digital",
                    description=f"Image {img.file_name} flagged as potentially manipulated (GAN: {img.gan_probability:.1f}%)",
                    risk_level="HIGH",
                    color="#ef4444"
                )
                self.state.scenarios.append(scenario)
        
        logger.info(f"Generated {len(self.state.scenarios)} scenarios")
    
    def _calculate_final_attribution(self):
        """Calculate final attribution with risk score."""
        
        # Find most connected/suspicious entity
        suspect_scores = {}
        
        for entity in self.state.entities:
            if entity.type == "PERSON":
                score = 0
                
                # Count mentions
                mentions = sum(1 for e in self.state.entities if e.name == entity.name)
                score += mentions * 10
                
                # Check graph centrality
                node_id = entity.name.lower().replace(" ", "_")
                if self.state.graph_metrics.get("top_brokers"):
                    if node_id in self.state.graph_metrics["top_brokers"][:3]:
                        score += 30
                
                # Check if linked to suspicious image
                for scenario in self.state.scenarios:
                    if scenario.entity == entity.name and scenario.risk_level == "HIGH":
                        score += 20
                
                suspect_scores[entity.name] = score
        
        if suspect_scores:
            top_suspect = max(suspect_scores, key=suspect_scores.get)
            top_score = suspect_scores[top_suspect]
            
            # Normalize to percentage
            max_possible = 100
            confidence = min((top_score / max_possible) * 100, 99.9)
            
            self.state.final_attribution = FinalAttribution(
                suspect=top_suspect,
                confidence_score=round(confidence, 1),
                role="Primary Suspect / Network Hub",
                evidence_summary=f"Identified through {len(self.state.text_analyses)} text analyses and {len(self.state.image_analyses)} image analyses",
                risk_breakdown={
                    "nlp_score": min(sum(t.threat_score for t in self.state.text_analyses), 100),
                    "image_score": sum(1 for i in self.state.image_analyses if not i.is_authentic) * 20,
                    "graph_score": len(self.state.graph_edges) * 5,
                    "location_score": len(self.state.locations) * 10
                }
            )
            
            self.state.overall_risk_score = confidence
        
        logger.info(f"Final attribution: {self.state.final_attribution}")
