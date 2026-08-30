
import subprocess
import json
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("MetadataExtractor")

class MetadataExtractor:
    """
    Wraps ExifTool to extract metadata from digital assets.
    """
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Runs ExifTool on the file and returns JSON metadata.
        """
        try:
            # Assuming exiftool is in PATH. If not, this needs full path.
            # -j for JSON output, -n for numeric values
            cmd = ["exiftool", "-j", "-n", file_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata_list = json.loads(result.stdout)
            
            if metadata_list:
                return metadata_list[0] # ExifTool returns a list [ {metadata} ]
            return {}
            
        except FileNotFoundError:
            logger.error("ExifTool not found in PATH.")
            return {"error": "ExifTool not installed"}
        except subprocess.CalledProcessError as e:
            logger.error(f"ExifTool failed: {e.stderr}")
            return {"error": "Extraction failed"}
