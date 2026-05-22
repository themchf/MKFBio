import pandas as pd
from Bio import SeqIO
import os

class BiologicalParser:
    def auto_detect_and_parse(self, file_obj) -> tuple[str, Any]:
        """Identifies file type and parses into structured memory."""
        file_name = file_obj.name.lower()
        
        # 1. Sequence Data
        if file_name.endswith(('.fasta', '.fa')):
            # Read fasta into a list of SeqRecords
            from io import StringIO
            stringio = StringIO(file_obj.getvalue().decode("utf-8"))
            records = list(SeqIO.parse(stringio, "fasta"))
            return "fasta", {"count": len(records), "records": records[:5]} # Store metadata
            
        # 2. Tabular / Differential Expression Data
        elif file_name.endswith('.csv'):
            df = pd.read_csv(file_obj)
            return "csv", df
            
        # 3. Variant Calls
        elif file_name.endswith('.vcf'):
            # In production, use PyVCF3 or pysam.VariantFile here
            return "vcf", "Parsed VCF metadata"
            
        # 4. Literature / Metadata
        elif file_name.endswith('.pdf'):
            # Use pdfplumber to extract text for RAG
            return "pdf", "Extracted text content"
            
        else:
            return "unknown", file_obj.read()
