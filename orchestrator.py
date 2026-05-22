from typing import List, Dict, Any
from src.parser import BiologicalParser
from src.explainer import ExplanationAgent

class ProcessOrchestrator:
    def __init__(self):
        self.parser = BiologicalParser()
        self.explainer = ExplanationAgent()

    def parse_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """Routes files to the correct parsing logic based on auto-detection."""
        parsed_collections = {}
        for file in uploaded_files:
            file_type, data = self.parser.auto_detect_and_parse(file)
            parsed_collections[file.name] = {
                "type": file_type,
                "data": data
            }
        return parsed_collections

    def analyze_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs deterministic stats (QC, p-values, fold changes)."""
        results = {"anomalies": [], "diff_expr": None}
        
        # Example logic: Look for tabular data to run differential expression
        for name, meta in parsed_data.items():
            if meta["type"] == "csv":
                # Mock analysis logic
                results["diff_expr"] = meta["data"] 
                # Add basic anomaly detection (e.g., low read counts)
                
        return results

    def generate_explanation(self, stats_results: Dict[str, Any]) -> Dict[str, Any]:
        """Passes the statistical findings to the LLM for biological context."""
        # This is where the AI does the heavy lifting
        return self.explainer.explain_results(stats_results)