"""
Geolocation Extraction Module
Extracts GPS coordinates and location metadata from images using EXIF data.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("GeoExtractor")

class GeoExtractor:
    """Extract geolocation data from image EXIF metadata."""
    
    def __init__(self):
        pass
    
    def _get_decimal_coords(self, gps_coords, gps_ref):
        """Convert GPS coordinates to decimal format."""
        try:
            degrees = float(gps_coords[0])
            minutes = float(gps_coords[1])
            seconds = float(gps_coords[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if gps_ref in ['S', 'W']:
                decimal = -decimal
            
            return round(decimal, 6)
        except Exception as e:
            logger.error(f"Coord conversion error: {e}")
            return None
    
    def extract_geotag(self, image_path: str) -> dict:
        """
        Extract geolocation data from image.
        
        Returns:
            dict with latitude, longitude, address info, and all EXIF metadata
        """
        result = {
            "has_geotag": False,
            "latitude": None,
            "longitude": None,
            "altitude": None,
            "timestamp": None,
            "device_info": {},
            "map_url": None,
            "all_exif": {}
        }
        
        try:
            if not os.path.exists(image_path):
                return {"error": f"File not found: {image_path}"}
            
            img = Image.open(image_path)
            exif_data = img._getexif()
            
            if not exif_data:
                result["error"] = "No EXIF data found"
                return result
            
            # Extract all EXIF tags
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # Skip binary data
                if isinstance(value, bytes):
                    continue
                
                # Handle GPS Info separately
                if tag == "GPSInfo":
                    gps_data = {}
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_value = value[gps_tag_id]
                        if not isinstance(gps_value, bytes):
                            gps_data[gps_tag] = str(gps_value) if not isinstance(gps_value, (int, float)) else gps_value
                    
                    # Extract coordinates
                    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                        lat_ref = gps_data["GPSLatitudeRef"]
                        lat = eval(gps_data["GPSLatitude"]) if isinstance(gps_data["GPSLatitude"], str) else gps_data["GPSLatitude"]
                        result["latitude"] = self._get_decimal_coords(lat, lat_ref)
                    
                    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                        lon_ref = gps_data["GPSLongitudeRef"]
                        lon = eval(gps_data["GPSLongitude"]) if isinstance(gps_data["GPSLongitude"], str) else gps_data["GPSLongitude"]
                        result["longitude"] = self._get_decimal_coords(lon, lon_ref)
                    
                    if "GPSAltitude" in gps_data:
                        result["altitude"] = gps_data["GPSAltitude"]
                    
                    if result["latitude"] and result["longitude"]:
                        result["has_geotag"] = True
                        result["map_url"] = f"https://www.google.com/maps?q={result['latitude']},{result['longitude']}"
                
                elif tag == "Make":
                    result["device_info"]["make"] = str(value)
                elif tag == "Model":
                    result["device_info"]["model"] = str(value)
                elif tag == "DateTime" or tag == "DateTimeOriginal":
                    result["timestamp"] = str(value)
                elif tag == "Software":
                    result["device_info"]["software"] = str(value)
                
                # Store in all_exif
                try:
                    result["all_exif"][tag] = str(value)[:200]  # Limit length
                except:
                    pass
            
            return result
            
        except Exception as e:
            logger.error(f"Geotag extraction failed: {e}")
            return {"error": str(e), "has_geotag": False}
    
    def extract_batch(self, image_paths: list) -> list:
        """Extract geotags from multiple images."""
        return [self.extract_geotag(path) for path in image_paths]


class FileRecoveryEngine:
    """
    Simple deleted file recovery simulation.
    Scans for recoverable file signatures in unallocated space.
    """
    
    # Common file signatures (magic bytes)
    SIGNATURES = {
        "JPEG": b'\xff\xd8\xff',
        "PNG": b'\x89PNG',
        "PDF": b'%PDF',
        "ZIP": b'PK\x03\x04',
        "DOCX": b'PK\x03\x04',
        "MP4": b'\x00\x00\x00\x18ftyp',
        "RAR": b'Rar!',
    }
    
    def __init__(self):
        pass
    
    def scan_directory(self, directory: str) -> dict:
        """
        Scan directory for deleted/hidden files.
        
        For demo purposes, simulates recovery analysis.
        In real forensics, this would scan unallocated disk space.
        """
        result = {
            "directory": directory,
            "recovered_files": [],
            "suspicious_files": [],
            "analysis_summary": {}
        }
        
        try:
            if not os.path.exists(directory):
                return {"error": f"Directory not found: {directory}"}
            
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    
                    try:
                        # Check file signature
                        with open(filepath, 'rb') as f:
                            header = f.read(20)
                        
                        detected_type = None
                        for ftype, sig in self.SIGNATURES.items():
                            if header.startswith(sig):
                                detected_type = ftype
                                break
                        
                        # Check for extension mismatch
                        ext = filename.split('.')[-1].upper() if '.' in filename else "NONE"
                        
                        if detected_type and ext != detected_type and ext != "DOCX" and detected_type != "DOCX":
                            result["suspicious_files"].append({
                                "path": filepath,
                                "claimed_type": ext,
                                "actual_type": detected_type,
                                "reason": "File extension mismatch with actual content"
                            })
                        
                        # Check for hidden files
                        if filename.startswith('.') or filename.startswith('~'):
                            result["suspicious_files"].append({
                                "path": filepath,
                                "claimed_type": ext,
                                "actual_type": detected_type or ext,
                                "reason": "Hidden or temporary file"
                            })
                        
                        # Track by type
                        if detected_type:
                            result["analysis_summary"][detected_type] = result["analysis_summary"].get(detected_type, 0) + 1
                        
                    except Exception as e:
                        continue
            
            result["total_scanned"] = sum(result["analysis_summary"].values())
            result["suspicious_count"] = len(result["suspicious_files"])
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_file(self, filepath: str) -> dict:
        """Analyze a single file for forensic artifacts."""
        result = {
            "filepath": filepath,
            "exists": False,
            "size_bytes": 0,
            "detected_type": None,
            "claimed_type": None,
            "metadata": {},
            "is_suspicious": False,
            "suspicion_reasons": []
        }
        
        try:
            if not os.path.exists(filepath):
                return result
            
            result["exists"] = True
            result["size_bytes"] = os.path.getsize(filepath)
            result["claimed_type"] = filepath.split('.')[-1].upper() if '.' in filepath else "NONE"
            
            with open(filepath, 'rb') as f:
                header = f.read(20)
            
            for ftype, sig in self.SIGNATURES.items():
                if header.startswith(sig):
                    result["detected_type"] = ftype
                    break
            
            if result["detected_type"] and result["claimed_type"] != result["detected_type"]:
                result["is_suspicious"] = True
                result["suspicion_reasons"].append("Extension mismatch")
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
