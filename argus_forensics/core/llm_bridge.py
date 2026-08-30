
import ollama
from .telemetry import Telemetry

logger = Telemetry.get_logger("LLM_Bridge")

class LLMBridge:
    """
    Interface for local Ollama instance (Llama 3 / Mistral).
    Handles generation of forensic narratives and psychological profiling.
    """
    
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.check_connection()

    def check_connection(self):
        try:
            # Simple list call to check if ollama is running
            ollama.list() 
            logger.info(f"Connected to Ollama. Using model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Ollama connection failed: {str(e)}. AI features may be disabled.")

    def generate_narrative(self, prompt: str, context: str = "") -> str:
        """
        Generates a narrative response from the LLM.
        """
        full_prompt = f"System: You are ARGUS, an elite digital forensics AI. {context}\nUser: {prompt}"
        
        try:
            response = ollama.generate(model=self.model_name, prompt=full_prompt)
            return response['response']
        except Exception as e:
            logger.error(f"LLM Generation failed: {str(e)}")
            return "[AI GENERATION FAILED]"

    def analyze_sentiment_intent(self, text: str) -> dict:
        """
        Uses LLM to analyze sentiment and radicalization intent.
        Returns a JSON-like dict (parsed from text).
        """
        prompt = (
            "Analyze the following text for: 1. Sentiment (Positive/Negative/Neutral), "
            "2. Aggression Level (0-10), 3. Radicalization Indicators (None/Low/High). "
            "Return ONLY a JSON object with keys: sentiment, aggression, radicalization. "
            f"Text: \"{text}\""
        )
        
        try:
            response = ollama.generate(model=self.model_name, prompt=prompt, format="json")
            # In updated ollama python client, format="json" ensures json output
            return response['response'] # Should be a JSON string
        except Exception as e:
            logger.error(f"LLM Analysis failed: {str(e)}")
            return {"error": str(e)}
