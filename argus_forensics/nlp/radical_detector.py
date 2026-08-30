
from ..core.llm_bridge import LLMBridge
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("RadicalDetector")

class RadicalDetector:
    """
    Uses LLM to detect radicalization attempts, hate speech, and dangerous intent.
    """
    
    def __init__(self):
        self.llm = LLMBridge()

    def analyze_risk(self, text_content: list[str]) -> dict:
        """
        Analyzes a list of posts/messages for aggregation risk.
        """
        # Concat a sample of text to stay within context window
        combined_text = "\n".join(text_content[:20]) 
        
        if not combined_text.strip():
            return {"risk_level": "UNKNOWN", "details": "No content to analyze"}

        result = self.llm.analyze_sentiment_intent(combined_text)
        
        # Basic parsing logic if the LLM returns structured dict
        # This depends on LLMBridge returning the raw dict from Ollama
        
        return {
            "analysis_engine": "Ollama_Llama3", # or configured model
            "raw_result": result
        }
