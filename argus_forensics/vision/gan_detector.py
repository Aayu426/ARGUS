"""
Deep Learning GAN/Deepfake Detector v2
Optimized for modern AI generators (DALL-E, Midjourney, Stable Diffusion)

Uses:
1. Pre-trained ResNet for feature extraction with calibrated thresholds
2. Color distribution analysis (AI images have specific color patterns)
3. DCT Frequency Analysis (upsampling artifacts)
4. Texture & uniformity analysis
"""

import os
import hashlib
import numpy as np
from PIL import Image
from io import BytesIO
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("GANDetector")

class GANDetector:
    """
    Advanced GAN/Deepfake detector optimized for modern AI generators.
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the detection model using pre-trained ResNet."""
        try:
            self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info(f"GAN Detector v2 initialized on {self.device}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self.model = None
    
    def analyze_image(self, image_path: str) -> dict:
        """Perform comprehensive AI detection analysis."""
        if not os.path.exists(image_path):
            return {"error": "Image not found", "ganProbability": 0}
        
        try:
            original = Image.open(image_path).convert('RGB')
            
            # Run multiple detection methods
            dl_score = self._deep_learning_analysis(original)
            color_score = self._color_analysis(original)
            freq_score = self._frequency_analysis(original)
            texture_score = self._texture_analysis(original)
            face_score = self._face_analysis(original)
            noise_scale_score = self._noise_scaling_analysis(original)
            
            # === Dynamic Optimization ===
            quality_score = self._estimate_image_quality(original)
            weights = self._optimize_parameters(quality_score)
            
            # === Resolution & compression safeguard ===
            min_dim = min(original.size)
            
            # 1. Ultra-Low Res (<200px): Data insufficient for trusted result.
            if min_dim < 200:
                 logger.info(f"Ultra-low resolution ({original.size}). Forcing scores to Authentic (Insufficient Data).")
                 # Cannot prove fake without data -> Presumption of Authenticity
                 dl_score = 45.0
                 color_score = 45.0
                 freq_score = 45.0 
                 texture_score = 45.0
                 face_score = 45.0 
                 noise_scale_score = 45.0
                 
            # 2. Low Res/Quality (<400px or Blur): Adaptive Dampening
            elif min_dim < 400 or quality_score < 0.4:
                logger.info(f"Low quality/res image detected (Q={quality_score:.2f}), dampening artifact scores")
                # Pull texture/freq/noise scores towards neutral (40-50)
                if texture_score > 50: texture_score = 50 + (texture_score - 50) * 0.3
                if freq_score > 50: freq_score = 50 + (freq_score - 50) * 0.3
                if noise_scale_score > 50: noise_scale_score = 50 + (noise_scale_score - 50) * 0.3

            combined_score = (
                dl_score * weights['dl'] + 
                color_score * weights['color'] + 
                freq_score * weights['freq'] + 
                texture_score * weights['texture'] +
                face_score * weights['face'] +
                noise_scale_score * weights['noise_scale']
            )
            
            gan_probability = float(min(max(combined_score, 5.0), 95.0))
            is_synthetic = gan_probability > 50
            
            # Granular Noise Levels
            if noise_scale_score < 30:
                noise_level = "NATURAL"      # Consistent sensor noise
            elif noise_scale_score < 55:
                noise_level = "PROCESSED"    # Compression or mild filtering
            elif noise_scale_score < 75:
                noise_level = "SUSPICIOUS"   # Inconsistent scaling
            else:
                noise_level = "SYNTHETIC"    # Strong generative artifacts
            
            if is_synthetic:
                warnings = [
                    {
                        "title": "SYNTHETIC CONTENT DETECTED", 
                        "desc": f"AI probability: {gan_probability:.1f}%. Scaling analysis indicates synthetic origin.", 
                        "type": "warning"
                    },
                    {
                        "title": "ANALYSIS BREAKDOWN", 
                        "desc": f"DL: {dl_score:.0f}% | Noise Scale: {noise_scale_score:.0f}% | Color: {color_score:.0f}%", 
                        "type": "warning"
                    }
                ]
            elif noise_level in ["SUSPICIOUS", "SYNTHETIC"] or texture_score > 65 or dl_score > 65:
                # Higher threshold (65) for manual warning if quality is low
                warnings = [
                    {
                        "title": "SUSPICIOUS INDICATORS", 
                        "desc": f"Probability ({gan_probability:.1f}%) is inconclusive, but anomalous noise/texture patterns were detected.", 
                        "type": "warning"
                    },
                    {
                        "title": "MANUAL REVIEW ADVISED", 
                        "desc": f"Noise Level: {noise_level}. Check for local editing or partial manipulation.", 
                        "type": "warning"
                    }
                ]
            else:
                auth_desc = "Probability: {gan_probability:.1f}%. Noise variance scales naturally."
                if quality_score < 0.4:
                    auth_desc += " (Low quality input detected - analysis adjusted)."
                    
                warnings = [
                    {
                        "title": "LIKELY AUTHENTIC", 
                        "desc": auth_desc.format(gan_probability=gan_probability), 
                        "type": "success"
                    }
                ]
            
            return {
                "ganProbability": round(gan_probability, 2),
                "noiseLevel": noise_level,
                "authentic": not is_synthetic,
                "warnings": warnings,
                "metadata": {
                    "format": image_path.split('.')[-1].upper() if '.' in image_path else "UNKNOWN",
                    "analyzed": True,
                    "dl_score": round(float(dl_score), 2),
                    "color_score": round(float(color_score), 2),
                    "noise_scale_score": round(float(noise_scale_score), 2),
                    "frequency_score": round(float(freq_score), 2),
                    "texture_score": round(float(texture_score), 2),
                    "face_score": round(float(face_score), 2),
                    "dimensions": f"{original.size[0]}x{original.size[1]}",
                    "device": str(self.device)
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "ganProbability": 50.0,
                "noiseLevel": "UNKNOWN",
                "authentic": False,
                "warnings": [{"title": "ANALYSIS ERROR", "desc": str(e), "type": "warning"}],
                "error": str(e)
            }
    
    def _deep_learning_analysis(self, image: Image.Image) -> float:
        """CNN feature analysis for anomaly detection."""
        if self.model is None:
            return 50.0
        
        try:
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(img_tensor)
                features_np = features.cpu().numpy().flatten()
                
                mean = np.mean(features_np)
                std = np.std(features_np)
                if std == 0:
                    return 50.0
                
                # Kurtosis analysis - recalibrated for modern AI
                kurtosis = float(np.mean(((features_np - mean) / std) ** 4))
                
                # Skewness analysis
                skewness = float(np.mean(((features_np - mean) / std) ** 3))
                
                # Modern AI images tend to have feature distributions that are:
                # - More uniform (lower kurtosis)
                # - Less extreme values
                score = 30.0  # Base score
                
                # Kurtosis-based scoring (recalibrated)
                if kurtosis < 2.5:
                    score += 40  # Strong indicator of AI
                elif kurtosis < 3.0:
                    score += 25
                elif kurtosis < 3.5:
                    score += 10
                    
                # Feature range analysis
                feature_range = np.max(features_np) - np.min(features_np)
                if feature_range < 5:
                    score += 20  # Narrow range suggests AI
                elif feature_range < 10:
                    score += 10
                
                return float(min(max(score, 5.0), 95.0))
                
        except Exception as e:
            logger.warning(f"Deep learning analysis failed: {e}")
            return 50.0
    
    def _color_analysis(self, image: Image.Image) -> float:
        """
        Analyze color distribution patterns.
        AI images often have characteristic color distributions.
        """
        try:
            arr = np.array(image)
            
            # Analyze each color channel
            scores = []
            
            for channel in range(3):
                channel_data = arr[:, :, channel].flatten()
                
                # Histogram analysis
                hist, _ = np.histogram(channel_data, bins=256, range=(0, 255))
                hist = hist / hist.sum()  # Normalize
                
                # Entropy (AI images often have specific entropy characteristics)
                entropy = -np.sum(hist * np.log2(hist + 1e-10))
                
                # Peak analysis - AI images often have smoother histograms
                peak_count = np.sum(hist > hist.mean() * 2)
                
                channel_score = 30.0
                
                # Low entropy indicates potential AI
                if entropy < 6.5:
                    channel_score += 30
                elif entropy < 7.0:
                    channel_score += 15
                
                # Few peaks indicates AI smoothness
                if peak_count < 20:
                    channel_score += 20
                elif peak_count < 40:
                    channel_score += 10
                    
                scores.append(channel_score)
            
            # Color coherence check
            r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            
            # AI images often have high RGB correlation
            rg_corr = np.corrcoef(r.flatten(), g.flatten())[0, 1]
            rb_corr = np.corrcoef(r.flatten(), b.flatten())[0, 1]
            
            avg_corr = (abs(rg_corr) + abs(rb_corr)) / 2
            if avg_corr > 0.9:
                for i in range(len(scores)):
                    scores[i] += 15
            
            return float(min(max(np.mean(scores), 5.0), 95.0))
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {e}")
            return 40.0
    
    def _frequency_analysis(self, image: Image.Image) -> float:
        """DCT frequency domain analysis for GAN artifacts."""
        try:
            gray = np.array(image.convert('L'), dtype=np.float32)
            
            # 2D FFT analysis
            fft = np.fft.fft2(gray)
            fft_shift = np.fft.fftshift(fft)
            magnitude = np.abs(fft_shift)
            
            h, w = magnitude.shape
            center_h, center_w = h // 2, w // 2
            
            # Radial frequency analysis
            y, x = np.ogrid[:h, :w]
            r = np.sqrt((y - center_h)**2 + (x - center_w)**2)
            
            # Analyze different frequency bands
            bands = [
                (0, min(h, w) * 0.1),      # Low freq
                (min(h, w) * 0.1, min(h, w) * 0.3),  # Mid freq
                (min(h, w) * 0.3, min(h, w) * 0.5),  # High freq
            ]
            
            band_energies = []
            for low, high in bands:
                mask = (r >= low) & (r < high)
                band_energy = np.mean(magnitude[mask]) if np.any(mask) else 0
                band_energies.append(band_energy)
            
            # AI images often have unusual mid-to-high frequency ratios
            if len(band_energies) >= 3 and band_energies[0] > 0:
                mid_ratio = band_energies[1] / band_energies[0]
                high_ratio = band_energies[2] / band_energies[0]
                
                score = 35.0
                
                # Unusual frequency patterns
                if mid_ratio > 0.1:
                    score += 25
                if high_ratio > 0.05:
                    score += 20
                    
                return float(min(max(score, 5.0), 95.0))
            
            return 40.0
            
        except Exception as e:
            logger.warning(f"Frequency analysis failed: {e}")
            return 40.0
    
    def _texture_analysis(self, image: Image.Image) -> float:
        """Analyze texture for AI-typical patterns."""
        try:
            gray = np.array(image.convert('L'), dtype=np.float32)
            
            # Block-based variance analysis
            block_size = 16
            h, w = gray.shape
            variances = []
            
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    variances.append(np.var(block))
            
            if len(variances) == 0:
                return 40.0
            
            # Coefficient of variation of block variances
            cv = np.std(variances) / (np.mean(variances) + 1e-10)
            
            score = 35.0
            
            # AI images tend to have more uniform textures
            if cv < 0.8:
                score += 35
            elif cv < 1.2:
                score += 20
            elif cv < 1.8:
                score += 10
            
            # Edge coherence check (AI images have unusual edge patterns)
            from scipy import ndimage
            edges = ndimage.sobel(gray)
            edge_var = np.var(edges)
            
            # Normalize edge variance by image variance
            normalized_edge_var = edge_var / (np.var(gray) + 1e-10)
            
            if normalized_edge_var < 0.5:
                score += 15
            
            return float(min(max(score, 5.0), 95.0))
            
        except ImportError:
            return self._simple_texture(image)
        except Exception as e:
            logger.warning(f"Texture analysis failed: {e}")
            return 40.0
    
    def _simple_texture(self, image: Image.Image) -> float:
        """Fallback texture analysis without scipy."""
        try:
            gray = np.array(image.convert('L'), dtype=np.float32)
            # Simple block variance
            block_size = 16
            h, w = gray.shape
            variances = []
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    variances.append(np.var(gray[i:i+block_size, j:j+block_size]))
            if variances:
                cv = np.std(variances) / (np.mean(variances) + 1e-10)
                return 50.0 if cv < 1.0 else 30.0
            return 40.0
        except:
            return 40.0
    
    def _face_analysis(self, image: Image.Image) -> float:
        """
        Analyze for AI-generated face characteristics.
        AI faces often have: symmetric features, unusual eye reflections, smooth skin.
        """
        try:
            arr = np.array(image)
            h, w = arr.shape[:2]
            
            score = 40.0  # Base score for face analysis
            
            # Symmetry analysis (AI faces are often too symmetric)
            left_half = arr[:, :w//2, :]
            right_half = np.flip(arr[:, w//2:, :], axis=1)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width, :]
            right_half = right_half[:, :min_width, :]
            
            # Compute symmetry score
            diff = np.abs(left_half.astype(float) - right_half.astype(float))
            symmetry = 1 - (np.mean(diff) / 255)
            
            # Very high symmetry is suspicious
            if symmetry > 0.85:
                score += 30
            elif symmetry > 0.75:
                score += 15
            
            # Skin smoothness check (focus on central region - likely face)
            center_region = arr[h//4:3*h//4, w//4:3*w//4, :]
            
            # Compute local variance in skin region
            skin_var = np.var(center_region)
            
            # AI faces often have unnaturally smooth skin
            if skin_var < 500:
                score += 20
            elif skin_var < 1000:
                score += 10
            
            return float(min(max(score, 5.0), 95.0))
            
        except Exception as e:
            logger.warning(f"Face analysis failed: {e}")
            return 40.0

    def _noise_scaling_analysis(self, image: Image.Image) -> float:
        """
        Analyze Noise Scaling Consistency.
        Checks if noise variance scales naturally when image is downsampled.
        Natural images: Noise variance drops by factor of ~4 when downscaled 2x (averaging).
        GANs/Upscalers: Noise/artifacts often persist or behave unnaturally across scales.
        """
        try:
            gray = np.array(image.convert('L'), dtype=np.float32)
            
            # 1. Extract noise from original (High pass filter)
            from scipy import ndimage
            
            # Simple noise extraction: Image - GaussianSmoothed(Image)
            # This captures high-freq noise
            smooth = ndimage.gaussian_filter(gray, sigma=1)
            noise_original = gray - smooth
            var_original = np.var(noise_original)
            
            if var_original == 0:
                return 50.0
            
            # 2. Downscale image 2x and extract noise
            # We use BOX average for natural downscaling simulation
            h, w = gray.shape
            # Ensure dimensions are even for reshaping
            h_even, w_even = h - (h % 2), w - (w % 2)
            gray_even = gray[:h_even, :w_even]
            
            # Block average (2x2 pooling)
            downscaled = gray_even.reshape(h_even//2, 2, w_even//2, 2).mean(axis=(1, 3))
            
            smooth_down = ndimage.gaussian_filter(downscaled, sigma=1)
            noise_down = downscaled - smooth_down
            var_down = np.var(noise_down)
            
            # 3. Compute Scaling Ratio
            # Theoretical ratio for natural sensor noise is ~4.0 (variance reduces by N pixels averaged)
            # However, due to gaussian smoothing separation, empirically it's often around 2.5-3.5 for real images
            ratio = var_original / (var_down + 1e-10)
            
            score = 25.0 # Base score (authentic)
            
            # AI/GANs often have ratio < 2.0 (noise persists too much) or > 6.0 (noise vanishes too fast / generated at specific scale)
            # Relaxed thresholds for JPEGs
            if ratio < 1.5:
                score = 85.0 # High suspicion: Noise is scale-invariant (synthetic texture)
            elif ratio < 1.9:
                score = 60.0
            elif ratio > 6.0:
                score = 60.0 # Suspicious: Noise disappears (smoothing artifacts)
            
            return float(min(max(score, 5.0), 95.0))
            
        except ImportError:
            return 40.0
        except Exception as e:
            logger.warning(f"Noise scaling analysis failed: {e}")
            return 40.0

    def _estimate_image_quality(self, image: Image.Image) -> float:
        """Estimate image quality score (0.0 to 1.0) based on blur and blocking."""
        try:
            from scipy import ndimage
            gray = np.array(image.convert('L'), dtype=np.float32)
            
            # 1. Blur detection (Laplacian variance)
            # High variance = sharp edges. Low variance = blur.
            # Using 3x3 Laplacian kernel via ndimage.laplace is standard.
            laplacian = ndimage.laplace(gray)
            blur_var = np.var(laplacian)
            
            # Theoretical max variance for sharp images is high (~1000+).
            # Low variance (<100) indicates blur.
            quality_blur = min(blur_var / 500.0, 1.0)
            
            # 2. JPEG artifact detection (simplified)
            # We assume blur metric correlates well with compression for now.
            
            return float(quality_blur)
        except Exception as e:
            logger.warning(f"Quality estimation failed: {e}")
            return 0.5  # Assume average quality on failure

    def _optimize_parameters(self, quality_score: float) -> dict:
        """Dynamically optimize thresholds based on image quality."""
        weights = {
            'dl': 0.20,
            'color': 0.15,
            'freq': 0.15, 
            'texture': 0.15,
            'face': 0.15,
            'noise_scale': 0.20
        }
        
        # If quality is low, trust Noise/Texture LESS (high false positive rate)
        if quality_score < 0.4:
            # Poor quality/Blurry
            logger.info("Optimizer: Low quality detected. Adjusting ensemble weights.")
            weights['texture'] = 0.05
            weights['freq'] = 0.05
            weights['noise_scale'] = 0.10
            weights['dl'] = 0.40   
            weights['face'] = 0.25 
            weights['color'] = 0.15 
            
        elif quality_score < 0.7:
             weights['noise_scale'] = 0.15
             weights['texture'] = 0.10
             weights['dl'] = 0.30
             
        return weights
