
import collections
import math
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("StylometryEngine")

class StylometryEngine:
    """
    Analyzes linguistic style markers (function words, punctuation, sentence length).
    Implements a simplified Burrows' Delta for authorship attribution.
    """
    
    def __init__(self):
        # Common English function words
        self.function_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at"
        ]

    def extract_features(self, text: str) -> dict:
        """
        Extracts stylometric features: function word usage, punctuation density.
        """
        tokens = text.lower().split()
        total_words = len(tokens)
        if total_words == 0:
            return {}
            
        # Function word frequencies
        counts = collections.Counter(tokens)
        frequencies = {
            word: counts[word] / total_words 
            for word in self.function_words
        }
        
        # Punctuation analysis
        punct_counts = {
            "!": text.count("!") / len(text) if len(text) > 0 else 0,
            "?": text.count("?") / len(text) if len(text) > 0 else 0,
            "...": text.count("...") / len(text) if len(text) > 0 else 0
        }
        
        return {**frequencies, **punct_counts}

    def compare_profiles(self, profile_a: dict, profile_b: dict) -> float:
        """
        Calculates similarity between two stylometric profiles (1.0 = identical).
        Uses simple Euclidean distance on feature vectors.
        """
        distance = 0.0
        keys = set(profile_a.keys()) | set(profile_b.keys())
        
        for k in keys:
            val_a = profile_a.get(k, 0)
            val_b = profile_b.get(k, 0)
            distance += (val_a - val_b) ** 2
            
        distance = math.sqrt(distance)
        
        # Normalize distance to similarity score (0-1 range approx)
        # Empirical scaling for demo
        similarity = 1.0 / (1.0 + distance * 10) 
        return similarity


class EnhancedStylometry:
    """
    PRD-compliant enhanced stylometry with character n-grams and pattern highlighting.
    Extends base functionality without modifying original StylometryEngine.
    """
    
    def __init__(self):
        self.base_engine = StylometryEngine()
    
    def extract_char_ngrams(self, text: str, n: int = 3) -> dict:
        """Extract character n-gram frequencies."""
        text_clean = text.lower().replace(" ", "_")
        if len(text_clean) < n:
            return {}
        
        ngrams = [text_clean[i:i+n] for i in range(len(text_clean) - n + 1)]
        counts = collections.Counter(ngrams)
        total = len(ngrams)
        
        # Return top 20 most frequent n-grams
        return {ng: count / total for ng, count in counts.most_common(20)}
    
    def extract_all_features(self, text: str) -> dict:
        """
        Comprehensive feature extraction for PRD compliance.
        Includes: base features + character n-grams + sentence metrics + punctuation patterns.
        """
        base_features = self.base_engine.extract_features(text)
        
        # Character n-grams (2-gram and 3-gram)
        char_2grams = self.extract_char_ngrams(text, 2)
        char_3grams = self.extract_char_ngrams(text, 3)
        
        # Enhanced punctuation analysis
        punct_pattern = {
            "exclamation_ratio": text.count("!") / max(len(text), 1),
            "question_ratio": text.count("?") / max(len(text), 1),
            "comma_ratio": text.count(",") / max(len(text), 1),
            "semicolon_ratio": text.count(";") / max(len(text), 1),
            "colon_ratio": text.count(":") / max(len(text), 1),
            "ellipsis_count": text.count("..."),
            "dash_ratio": text.count("-") / max(len(text), 1),
        }
        
        # Sentence-level metrics
        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        sentence_metrics = {
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(sentence_lengths) / max(len(sentence_lengths), 1),
            "sentence_length_variance": self._variance(sentence_lengths),
            "short_sentences_ratio": sum(1 for l in sentence_lengths if l < 5) / max(len(sentence_lengths), 1),
            "long_sentences_ratio": sum(1 for l in sentence_lengths if l > 20) / max(len(sentence_lengths), 1),
        }
        
        # Word-level metrics
        words = text.split()
        word_lengths = [len(w) for w in words]
        
        word_metrics = {
            "avg_word_length": sum(word_lengths) / max(len(word_lengths), 1),
            "word_length_variance": self._variance(word_lengths),
            "long_words_ratio": sum(1 for l in word_lengths if l > 8) / max(len(word_lengths), 1),
        }
        
        return {
            "base_features": base_features,
            "char_2grams": char_2grams,
            "char_3grams": char_3grams,
            "punctuation": punct_pattern,
            "sentence_metrics": sentence_metrics,
            "word_metrics": word_metrics,
        }
    
    def _variance(self, values: list) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def highlight_patterns(self, text: str) -> dict:
        """
        Identify and highlight distinctive linguistic patterns.
        Returns pattern markers for UI highlighting.
        """
        patterns = []
        
        # Find repeated phrases (2+ words)
        words = text.lower().split()
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            count = text.lower().count(phrase)
            if count > 1:
                patterns.append({"type": "repeated_phrase", "text": phrase, "count": count})
        
        # Find unusual punctuation patterns
        if "!!" in text:
            patterns.append({"type": "emphasis", "text": "!!", "count": text.count("!!")})
        if "???" in text or "?!" in text:
            patterns.append({"type": "intense_questioning", "text": "??/?!", "count": text.count("???") + text.count("?!")})
        if text.count("...") > 2:
            patterns.append({"type": "trailing_thought", "text": "...", "count": text.count("...")})
        
        # Capitalization patterns
        caps_words = [w for w in text.split() if w.isupper() and len(w) > 1]
        if caps_words:
            patterns.append({"type": "caps_emphasis", "text": ", ".join(caps_words[:5]), "count": len(caps_words)})
        
        # Unique stylistic markers
        unique_markers = []
        if text.count("—") > 0:
            unique_markers.append("em-dash usage")
        if text.count("'") > text.count('"'):
            unique_markers.append("single-quote preference")
        if text.count(";") > 2:
            unique_markers.append("semicolon heavy")
        
        return {
            "patterns": patterns[:10],  # Limit to top 10
            "unique_markers": unique_markers,
            "pattern_count": len(patterns)
        }
    
    def compute_similarity(self, features_a: dict, features_b: dict) -> float:
        """
        Enhanced similarity computation using multiple feature sets.
        """
        scores = []
        
        # Base feature similarity
        base_sim = self.base_engine.compare_profiles(
            features_a.get("base_features", {}),
            features_b.get("base_features", {})
        )
        scores.append(("base", base_sim, 0.3))
        
        # N-gram similarity (Jaccard-like)
        ngrams_a = set(features_a.get("char_3grams", {}).keys())
        ngrams_b = set(features_b.get("char_3grams", {}).keys())
        if ngrams_a or ngrams_b:
            ngram_sim = len(ngrams_a & ngrams_b) / max(len(ngrams_a | ngrams_b), 1)
            scores.append(("ngram", ngram_sim, 0.3))
        
        # Punctuation pattern similarity
        punct_a = features_a.get("punctuation", {})
        punct_b = features_b.get("punctuation", {})
        punct_diff = sum(abs(punct_a.get(k, 0) - punct_b.get(k, 0)) for k in set(punct_a) | set(punct_b))
        punct_sim = 1.0 / (1.0 + punct_diff * 100)
        scores.append(("punct", punct_sim, 0.2))
        
        # Sentence metric similarity
        sent_a = features_a.get("sentence_metrics", {})
        sent_b = features_b.get("sentence_metrics", {})
        sent_diff = abs(sent_a.get("avg_sentence_length", 0) - sent_b.get("avg_sentence_length", 0))
        sent_sim = 1.0 / (1.0 + sent_diff * 0.1)
        scores.append(("sentence", sent_sim, 0.2))
        
        # Weighted average
        total_weight = sum(w for _, _, w in scores)
        weighted_sim = sum(s * w for _, s, w in scores) / total_weight
        
        return round(weighted_sim * 100, 1)

