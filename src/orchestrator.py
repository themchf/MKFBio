from typing import List, Dict, Any, Tuple
import os

try:
    from .parser import BiologicalParser
    from .explainer import ExplanationAgent
except (ImportError, ValueError):
    from parser import BiologicalParser
    from explainer import ExplanationAgent

class ProcessOrchestrator:
    def __init__(self):
        self.parser = BiologicalParser()
        self.explainer = ExplanationAgent()

    def execution_flow(self, uploaded_files: List[Any], api_key: str = None) -> Dict[str, Any]:
        """Runs the parsing, calculations, and RAG compilation steps sequentially."""
        if not uploaded_files:
            return {}
            
        # Target the primary active file uploaded by the user
        primary_file = uploaded_files[0]
        data_type, parsed_meta = self.parser.auto_detect_and_parse(primary_file)
        
        # Build explanation out using real file outputs
        report_data = self.explainer.compose_dynamic_analysis(data_type, parsed_meta, api_key)
        
        # Pack the processing artifacts together to feed into app.py
        report_data["data_type"] = data_type
        report_data["raw_meta"] = parsed_meta
        report_data["anomalies"] = parsed_meta.get("anomalies", [])
        
        return report_data
