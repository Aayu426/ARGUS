
import hashlib
import os

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

class DualHasher:
    """
    Implements NIST-compliant dual hashing for digital evidence.
    Uses SHA3-512 (Primary) and SHA-256 (Secondary) to ensure collision resistance.
    """
    
    @staticmethod
    def calculate_hashes(file_path: str) -> dict:
        """
        Calculates SHA3-512 and SHA-256 hashes of a file in a single pass.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            dict: Dictionary containing 'sha3_512' and 'sha256' hex digests.
        """
        sha3 = hashlib.sha3_512()
        sha2 = hashlib.sha256()
        
        chunk_size = 65536 # 64KB chunks
        
        try:
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    sha3.update(data)
                    sha2.update(data)
                    
            return {
                "sha3_512": sha3.hexdigest(),
                "sha256": sha2.hexdigest()
            }
        except FileNotFoundError:
            raise FileNotFoundError(f"Evidence file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Hashing failed: {str(e)}")

    @staticmethod
    def verify_hashes(file_path: str, original_hashes: dict) -> bool:
        """
        Verifies if the current file hashes match the original records.
        """
        current_hashes = DualHasher.calculate_hashes(file_path)
        return (current_hashes["sha3_512"] == original_hashes.get("sha3_512") and
                current_hashes["sha256"] == original_hashes.get("sha256"))


class TripleHasher:
    """
    Extended hasher that includes BLAKE3 for PRD compliance.
    Uses SHA3-512 + SHA-256 + BLAKE3 for maximum forensic integrity.
    """
    
    @staticmethod
    def calculate_all_hashes(file_path: str) -> dict:
        """
        Calculates all three hash algorithms in a single file pass.
        """
        sha3 = hashlib.sha3_512()
        sha2 = hashlib.sha256()
        b3 = blake3.blake3() if BLAKE3_AVAILABLE else None
        
        chunk_size = 65536
        
        try:
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    sha3.update(data)
                    sha2.update(data)
                    if b3:
                        b3.update(data)
                    
            result = {
                "sha3_512": sha3.hexdigest(),
                "sha256": sha2.hexdigest(),
            }
            if b3:
                result["blake3"] = b3.hexdigest()
            else:
                result["blake3"] = "BLAKE3_NOT_INSTALLED"
            
            return result
        except FileNotFoundError:
            raise FileNotFoundError(f"Evidence file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Hashing failed: {str(e)}")

    @staticmethod
    def verify_all_hashes(file_path: str, original_hashes: dict) -> dict:
        """
        Verifies all hashes and returns detailed status.
        """
        current = TripleHasher.calculate_all_hashes(file_path)
        return {
            "sha3_512": {"match": current["sha3_512"] == original_hashes.get("sha3_512"), "current": current["sha3_512"][:16] + "..."},
            "sha256": {"match": current["sha256"] == original_hashes.get("sha256"), "current": current["sha256"][:16] + "..."},
            "blake3": {"match": current.get("blake3") == original_hashes.get("blake3"), "current": current.get("blake3", "N/A")[:16] + "..."},
            "overall": current["sha3_512"] == original_hashes.get("sha3_512") and current["sha256"] == original_hashes.get("sha256")
        }

