
import logging
import time
import functools
import json
from datetime import datetime

# Configure base logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("argus_execution.log"), # Disabled to prevent reload loop
        logging.StreamHandler()
    ]
)

class Telemetry:
    """
    Centralized logging and telemetry for Project ARGUS.
    """
    
    @staticmethod
    def get_logger(name: str):
        return logging.getLogger(f"ARGUS.{name}")

    @staticmethod
    def trace(func):
        """Decorator to trace function execution time and arguments."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("ARGUS.Trace")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"EXEC: {func.__name__} | Time: {duration:.4f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"FAIL: {func.__name__} | Time: {duration:.4f}s | Error: {str(e)}")
                raise e
        return wrapper

    @staticmethod
    def log_audit(event_type: str, details: dict):
        """
        Logs a high-level audit event (separate from technical logs).
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        # writing to a separate JSONL for structured audit
        with open("audit_trace.jsonl", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
