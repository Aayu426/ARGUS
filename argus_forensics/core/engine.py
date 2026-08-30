
from .telemetry import Telemetry
from ..integrity.chain_of_custody import ChainOfCustody
from ..ingestion.metadata_extractor import MetadataExtractor
from ..ingestion.temporal_analyzer import TemporalAnalyzer
from ..nlp.stylometry_engine import StylometryEngine
from ..nlp.radical_detector import RadicalDetector
from ..nlp.authorship_matcher import AuthorshipMatcher
from ..vision.gan_detector import GANDetector
from ..integrity.enhanced_report_gen import EnhancedReportGenerator

logger = Telemetry.get_logger("ArgusEngine")

class ArgusEngine:
    """
    Main controller for the forensic pipeline.
    """
    
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.custody = ChainOfCustody(case_id)
        self.metadata_ext = MetadataExtractor()
        self.temporal = TemporalAnalyzer()
        self.stylometry = StylometryEngine()
        self.radical = RadicalDetector()
        self.matcher = AuthorshipMatcher()
        self.gan_chk = GANDetector()
        self.reporter = EnhancedReportGenerator()
        
        logger.info(f"Engine initialized for Case {case_id}")

    def ingest_evidence(self, file_path: str):
        """
        Step 1: Secure Ingestion
        """
        block_id = self.custody.log_evidence(file_path, "USER_UPLOAD")
        logger.info(f"Evidence ingrained. Block: {block_id}")
        return block_id

    def analyze_artifact(self, file_path: str, artifact_type: str = "image"):
        """
        Step 2: Analysis Pipeline
        """
        results = {}
        
        # 1. Metadata
        meta = self.metadata_ext.extract_metadata(file_path)
        results["metadata"] = meta
        
        # 2. Type specific
        if artifact_type == "image":
            vision_res = self.gan_chk.analyze_image(file_path)
            results["vision"] = vision_res
            
        elif artifact_type == "text":
             # assumed file contains text
             with open(file_path, 'r') as f:
                 content = f.read()
             
             results["stylometry"] = self.stylometry.extract_features(content)
             results["radicalization"] = self.radical.analyze_risk([content])
        
        # Log analysis step
        self.custody.log_action("ANALYSIS_COMPLETE", {"artifact": file_path, "modules_run": list(results.keys())})
        
        return results

    def generate_final_report(self, analysis_results: dict):
        """
        Step 3: Reporting
        """
        path = f"Report_{self.case_id}.pdf"
        self.reporter.generate_full_report(self.case_id, analysis_results, path)
        self.custody.log_action("REPORT_GENERATED", {"path": path})
        return path
