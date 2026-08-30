
import pandas as pd
import numpy as np
from datetime import datetime
from ..core.telemetry import Telemetry

logger = Telemetry.get_logger("TemporalAnalyzer")

class TemporalAnalyzer:
    """
    Analyzes posting times to infer probable timezones and sleep patterns (circadian rhythm).
    """
    
    def analyze_timestamps(self, timestamps: list[datetime]) -> dict:
        """
        Takes a list of datetime objects (assumed UTC) and returns probable timezone offsets.
        """
        if not timestamps:
            return {"error": "No timestamps provided"}
            
        df = pd.DataFrame(timestamps, columns=["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        
        # Calculate hourly activity frequency
        hourly_counts = df["hour"].value_counts().sort_index().reindex(range(24), fill_value=0)
        
        # Simple heuristic: Sleep usually happens 00:00 - 06:00 local time.
        # We try to align the 'quietest' block of 6 hours with 00:00-06:00.
        
        best_offset = 0
        min_activity = float("inf")
        
        # Test all 24 hour offsets
        for offset in range(-12, 13):
            # Shift hours by offset
            shifted_counts = np.roll(hourly_counts.values, offset)
            # Sum activity in "sleep window" (indices 0-6 after shift)
            sleep_activity = sum(shifted_counts[0:6])
            
            if sleep_activity < min_activity:
                min_activity = sleep_activity
                best_offset = offset
                
        return {
            "probable_timezone_offset": best_offset,
            "hourly_heatmap": hourly_counts.to_dict(),
            "inferred_sleep_window_activity": int(min_activity)
        }
