
import json
import time
import os
from threading import Lock
from .hasher import DualHasher
import hashlib
import uuid

class ChainOfCustody:
    """
    Maintains an immutable, append-only log of all forensic actions.
    Uses a simple ledger where each entry is linked to the previous one via hash
    to form a tamper-evident chain (Merkle-chain style).
    """
    
    def __init__(self, case_id: str, ledger_path: str = "custody_ledger.jsonl"):
        self.case_id = case_id
        self.ledger_path = ledger_path
        self._lock = Lock()
        
        # Initialize ledger if not exists
        if not os.path.exists(self.ledger_path):
            self._init_ledger()

    def _init_ledger(self):
        genesis_block = {
            "block_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "action": "CASE_INITIALIZED",
            "actor": "ARGUS_SYSTEM",
            "details": f"Case {self.case_id} initialized",
            "prev_hash": "0" * 128
        }
        self._write_entry(genesis_block)

    def _get_last_entry(self) -> dict:
        """Reads the last line of the JSONL ledger."""
        if not os.path.exists(self.ledger_path):
            return None
            
        with open(self.ledger_path, "r") as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1])
        return None

    def _write_entry(self, entry: dict):
        """Writes entry to ledger atomically."""
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_action(self, action: str, details: dict, actor: str = "ARGUS_AUTOMATED"):
        """
        Logs a forensic action to the chain.
        """
        with self._lock:
            last_entry = self._get_last_entry()
            prev_hash = "0" * 128
            if last_entry:
                # Calculate hash of the previous entry to link them
                prev_text = json.dumps(last_entry, sort_keys=True)
                prev_hash = hashlib.sha3_512(prev_text.encode()).hexdigest()
            
            entry = {
                "block_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "action": action,
                "actor": actor,
                "details": details,
                "prev_hash": prev_hash
            }
            self._write_entry(entry)
            return entry["block_id"]

    def log_evidence(self, file_path: str, source: str):
        """
        Logs new evidence ingestion. Calculates hashes and adds to chain.
        """
        hashes = DualHasher.calculate_hashes(file_path)
        details = {
            "file_path": file_path,
            "source": source,
            "hashes": hashes
        }
        return self.log_action("EVIDENCE_ACQUIRED", details)

    def verify_chain(self) -> bool:
        """
        Validates the integrity of the entire chain of custody.
        """
        with self._lock:
            if not os.path.exists(self.ledger_path):
                return False
                
            with open(self.ledger_path, "r") as f:
                lines = [json.loads(line) for line in f]
                
            if not lines:
                return False
                
            for i in range(1, len(lines)):
                prev_entry = lines[i-1]
                curr_entry = lines[i]
                
                # Reconstruct hash of prev_entry
                prev_text = json.dumps(prev_entry, sort_keys=True)
                computed_prev_hash = hashlib.sha3_512(prev_text.encode()).hexdigest()
                
                if curr_entry["prev_hash"] != computed_prev_hash:
                    print(f"INTEGRITY FAILURE at block {i}: {curr_entry['block_id']}")
                    return False
                    
            return True
