
from .stylometry_engine import StylometryEngine
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("AuthorshipMatcher")

class AuthorshipMatcher:
    """
     matches unknown text against a database of known suspect profiles.
    """
    
    def __init__(self):
        self.engine = StylometryEngine()
        self.suspect_profiles = {} # id -> feature_dict

    def train_profile(self, suspect_id: str, texts: list[str]):
        """
        Builds a stylometric profile for a suspect.
        """
        full_text = " ".join(texts)
        features = self.engine.extract_features(full_text)
        self.suspect_profiles[suspect_id] = features
        logger.info(f"Trained profile for {suspect_id}")

    def identify_author(self, unknown_text: str) -> dict:
        """
        Compares unknown text against all trained profiles.
        Returns sorted matches.
        """
        unknown_features = self.engine.extract_features(unknown_text)
        matches = []
        
        for suspect_id, profile in self.suspect_profiles.items():
            similarity = self.engine.compare_profiles(unknown_features, profile)
            matches.append({"suspect_id": suspect_id, "similarity": similarity})
            
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches
