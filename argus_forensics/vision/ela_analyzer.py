"""
Error Level Analysis (ELA) Module for Image Manipulation Detection
PRD Module 4: Visual Authenticity

Detects image manipulation by analyzing JPEG compression artifacts.
Manipulated regions show different error levels compared to original content.
"""

import numpy as np
from PIL import Image
from io import BytesIO
import os
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("ELAAnalyzer")

class ELAAnalyzer:
    """
    Error Level Analysis for detecting image manipulation.
    
    ELA works by re-saving the image at a known quality level and comparing
    the difference. Manipulated areas typically show brighter error levels
    because they've been compressed at different quality levels.
    """
    
    def __init__(self, quality: int = 90, scale: int = 15):
        """
        Initialize ELA analyzer.
        
        Args:
            quality: JPEG quality for re-compression (default 90)
            scale: Error amplification scale for visualization (default 15)
        """
        self.quality = quality
        self.scale = scale
    
    def compute_ela(self, image_path: str) -> dict:
        """
        Compute Error Level Analysis on an image.
        
        Returns:
            dict with ela_array, metrics, and risk assessment
        """
        try:
            # Load original image
            original = Image.open(image_path).convert('RGB')
            
            # Re-save at specified quality
            buffer = BytesIO()
            original.save(buffer, 'JPEG', quality=self.quality)
            buffer.seek(0)
            resaved = Image.open(buffer).convert('RGB')
            
            # Compute difference
            original_arr = np.array(original, dtype=np.float32)
            resaved_arr = np.array(resaved, dtype=np.float32)
            
            ela_arr = np.abs(original_arr - resaved_arr)
            
            # Scale for visibility
            ela_scaled = np.clip(ela_arr * self.scale, 0, 255).astype(np.uint8)
            
            # Compute metrics
            metrics = self._compute_metrics(ela_arr)
            
            # Generate risk assessment
            risk = self._assess_risk(metrics)
            
            return {
                "ela_array": ela_scaled,
                "metrics": metrics,
                "risk": risk,
                "image_size": original.size
            }
            
        except Exception as e:
            logger.error(f"ELA computation failed: {e}")
            return {"error": str(e)}
    
    def _compute_metrics(self, ela_arr: np.ndarray) -> dict:
        """Compute statistical metrics from ELA array."""
        # Per-channel and overall statistics
        mean_error = float(np.mean(ela_arr))
        max_error = float(np.max(ela_arr))
        std_error = float(np.std(ela_arr))
        
        # Detect high-error regions (potential manipulation)
        threshold = mean_error + 2 * std_error
        high_error_ratio = float(np.sum(ela_arr > threshold) / ela_arr.size)
        
        # Detect very bright spots (strong manipulation indicators)
        very_high_threshold = mean_error + 3 * std_error
        hotspot_ratio = float(np.sum(ela_arr > very_high_threshold) / ela_arr.size)
        
        # Edge irregularity (manipulated regions often have sharp ELA edges)
        ela_gray = np.mean(ela_arr, axis=2) if len(ela_arr.shape) == 3 else ela_arr
        gradient_x = np.abs(np.diff(ela_gray, axis=1))
        gradient_y = np.abs(np.diff(ela_gray, axis=0))
        edge_intensity = float(np.mean(gradient_x) + np.mean(gradient_y))
        
        return {
            "mean_error": round(mean_error, 3),
            "max_error": round(max_error, 3),
            "std_error": round(std_error, 3),
            "high_error_ratio": round(high_error_ratio * 100, 2),
            "hotspot_ratio": round(hotspot_ratio * 100, 2),
            "edge_intensity": round(edge_intensity, 3)
        }
    
    def _assess_risk(self, metrics: dict) -> dict:
        """Assess manipulation risk based on ELA metrics."""
        score = 0
        reasons = []
        
        # High mean error suggests manipulation
        if metrics["mean_error"] > 15:
            score += 25
            reasons.append("Elevated mean error level")
        elif metrics["mean_error"] > 10:
            score += 15
            reasons.append("Moderate error level detected")
        
        # High standard deviation indicates inconsistent compression
        if metrics["std_error"] > 20:
            score += 25
            reasons.append("Inconsistent compression artifacts")
        elif metrics["std_error"] > 12:
            score += 15
            reasons.append("Slight compression inconsistencies")
        
        # Hotspots indicate localized manipulation
        if metrics["hotspot_ratio"] > 1.0:
            score += 30
            reasons.append("Significant hotspots detected")
        elif metrics["hotspot_ratio"] > 0.3:
            score += 20
            reasons.append("Minor hotspots present")
        
        # Edge intensity from manipulation boundaries
        if metrics["edge_intensity"] > 5:
            score += 20
            reasons.append("Sharp ELA boundaries detected")
        
        # Determine risk level
        if score >= 60:
            level = "HIGH"
        elif score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            "score": min(score, 100),
            "level": level,
            "reasons": reasons,
            "verdict": "LIKELY MANIPULATED" if score >= 50 else "POSSIBLY EDITED" if score >= 25 else "APPEARS AUTHENTIC"
        }
    
    def generate_heatmap(self, image_path: str, output_path: str = None) -> str:
        """
        Generate ELA heatmap visualization.
        
        Args:
            image_path: Path to input image
            output_path: Path for output heatmap (auto-generated if None)
            
        Returns:
            Path to saved heatmap image
        """
        result = self.compute_ela(image_path)
        
        if "error" in result:
            return None
        
        ela_arr = result["ela_array"]
        
        # Create heatmap using colormap
        try:
            import cv2
            
            # Convert to grayscale for heatmap
            ela_gray = np.mean(ela_arr, axis=2).astype(np.uint8)
            
            # Apply colormap (COLORMAP_JET for red-blue heat visualization)
            heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
            
            # Generate output path
            if output_path is None:
                base = os.path.splitext(image_path)[0]
                output_path = f"{base}_ela_heatmap.png"
            
            cv2.imwrite(output_path, heatmap)
            logger.info(f"ELA heatmap saved to {output_path}")
            
            return output_path
            
        except ImportError:
            # Fallback without OpenCV: save raw ELA image
            logger.warning("OpenCV not available, saving raw ELA")
            ela_img = Image.fromarray(ela_arr)
            
            if output_path is None:
                base = os.path.splitext(image_path)[0]
                output_path = f"{base}_ela.png"
            
            ela_img.save(output_path)
            return output_path
    
    def full_analysis(self, image_path: str, save_heatmap: bool = True) -> dict:
        """
        Perform full ELA analysis with all outputs.
        
        Returns:
            Complete analysis dict with metrics, risk, and heatmap path
        """
        result = self.compute_ela(image_path)
        
        if "error" in result:
            return result
        
        output = {
            "metrics": result["metrics"],
            "risk": result["risk"],
            "image_size": list(result["image_size"]),  # Convert tuple to list for JSON
            "analysis_quality": self.quality
        }
        
        if save_heatmap:
            heatmap_path = self.generate_heatmap(image_path)
            output["heatmap_path"] = heatmap_path
        
        return output


class ManipulationDetector:
    """
    Combined manipulation detection using multiple techniques.
    Aggregates ELA + frequency analysis for comprehensive assessment.
    """
    
    def __init__(self):
        self.ela = ELAAnalyzer()
    
    def detect(self, image_path: str) -> dict:
        """
        Run full manipulation detection pipeline.
        """
        results = {
            "image_path": image_path,
            "analyses": {}
        }
        
        # ELA Analysis
        ela_result = self.ela.full_analysis(image_path, save_heatmap=True)
        results["analyses"]["ela"] = ela_result
        
        # DCT Block Analysis
        dct_result = self._dct_block_analysis(image_path)
        results["analyses"]["dct"] = dct_result
        
        # Copy-Move Detection (simplified)
        copymove_result = self._copy_move_detection(image_path)
        results["analyses"]["copy_move"] = copymove_result
        
        # Aggregate final verdict
        results["final_verdict"] = self._aggregate_verdict(results["analyses"])
        
        return results
    
    def _dct_block_analysis(self, image_path: str) -> dict:
        """
        Analyze DCT block artifacts.
        JPEG images are compressed in 8x8 blocks; double compression 
        creates detectable ghost artifacts.
        """
        try:
            img = Image.open(image_path).convert('L')
            arr = np.array(img, dtype=np.float32)
            
            # Check for 8x8 blocking artifacts
            h, w = arr.shape
            block_scores = []
            
            for y in range(0, h - 8, 8):
                for x in range(0, w - 8, 8):
                    block = arr[y:y+8, x:x+8]
                    # Edge energy within block
                    edge = np.std(block)
                    block_scores.append(edge)
            
            if not block_scores:
                return {"score": 0, "level": "UNKNOWN"}
            
            avg_block_energy = float(np.mean(block_scores))
            block_variance = float(np.var(block_scores))
            
            # High variance in block energy suggests manipulation
            score = 0
            if block_variance > 500:
                score = 70
            elif block_variance > 200:
                score = 40
            else:
                score = 15
            
            return {
                "avg_block_energy": round(avg_block_energy, 2),
                "block_variance": round(block_variance, 2),
                "score": int(score),
                "level": "HIGH" if score > 50 else "MEDIUM" if score > 25 else "LOW"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _copy_move_detection(self, image_path: str) -> dict:
        """
        Simplified copy-move forgery detection.
        Looks for repeated patterns that might indicate copied regions.
        """
        try:
            img = Image.open(image_path).convert('L')
            arr = np.array(img)
            
            # Simplified: check for identical block regions
            h, w = arr.shape
            block_size = 16
            block_hashes = {}
            duplicates = 0
            
            for y in range(0, h - block_size, block_size // 2):
                for x in range(0, w - block_size, block_size // 2):
                    block = arr[y:y+block_size, x:x+block_size]
                    block_hash = hash(block.tobytes())
                    
                    if block_hash in block_hashes:
                        duplicates += 1
                    else:
                        block_hashes[block_hash] = (x, y)
            
            total_blocks = len(block_hashes) + duplicates
            dup_ratio = float(duplicates) / max(total_blocks, 1)
            
            return {
                "duplicate_blocks": int(duplicates),
                "duplicate_ratio": round(dup_ratio * 100, 2),
                "level": "HIGH" if dup_ratio > 0.05 else "MEDIUM" if dup_ratio > 0.02 else "LOW",
                "note": "High duplicate ratio may indicate copy-move forgery" if dup_ratio > 0.03 else "No significant duplicates"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _aggregate_verdict(self, analyses: dict) -> dict:
        """Combine all analysis results into final verdict."""
        scores = []
        all_reasons = []
        
        # ELA contribution
        if "ela" in analyses and "risk" in analyses["ela"]:
            ela_score = analyses["ela"]["risk"].get("score", 0)
            scores.append(ela_score * 0.5)  # 50% weight
            all_reasons.extend(analyses["ela"]["risk"].get("reasons", []))
        
        # DCT contribution
        if "dct" in analyses:
            dct_score = analyses["dct"].get("score", 0)
            scores.append(dct_score * 0.3)  # 30% weight
        
        # Copy-move contribution
        if "copy_move" in analyses:
            cm_level = analyses["copy_move"].get("level", "LOW")
            cm_score = 70 if cm_level == "HIGH" else 35 if cm_level == "MEDIUM" else 10
            scores.append(cm_score * 0.2)  # 20% weight
        
        final_score = sum(scores)
        
        if final_score >= 55:
            level = "HIGH"
            verdict = "LIKELY MANIPULATED"
        elif final_score >= 30:
            level = "MEDIUM"
            verdict = "POSSIBLY EDITED"
        else:
            level = "LOW"
            verdict = "APPEARS AUTHENTIC"
        
        return {
            "manipulation_score": round(final_score, 1),
            "risk_level": level,
            "verdict": verdict,
            "contributing_factors": all_reasons[:5]  # Top 5 reasons
        }
