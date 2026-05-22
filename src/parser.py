import pandas as pd
import numpy as np
from Bio import SeqIO
from io import StringIO
from typing import Dict, Any, Tuple

class BiologicalParser:
    def auto_detect_and_parse(self, file_obj) -> Tuple[str, Dict[str, Any]]:
        """Identifies file type, extracts true biological matrices, and profiles metrics."""
        file_name = file_obj.name.lower()
        content_bytes = file_obj.getvalue()
        
        # 1. FASTA Parsing (Real computation of GC Content & Lengths)
        if file_name.endswith(('.fasta', '.fa', '.fna')):
            text_data = content_bytes.decode("utf-8")
            records = list(SeqIO.parse(StringIO(text_data), "fasta"))
            
            sequence_metrics = []
            for rec in records:
                seq_str = str(rec.seq).upper()
                seq_len = len(seq_str)
                gc_cnt = seq_str.count('G') + seq_str.count('C')
                gc_content = (gc_cnt / seq_len) * 100 if seq_len > 0 else 0
                sequence_metrics.append({
                    "id": rec.id,
                    "length": seq_len,
                    "gc_content": round(gc_content, 2)
                })
                
            return "fasta", {
                "summary": {"total_sequences": len(records)},
                "metrics": pd.DataFrame(sequence_metrics)
            }
            
        # 2. Expression / Tabular Data (Flexible Column Matching)
        elif file_name.endswith(('.csv', '.tsv', '.txt')):
            sep = '\t' if file_name.endswith('.tsv') else ','
            try:
                df = pd.read_csv(StringIO(content_bytes.decode("utf-8")), sep=sep)
            except Exception:
                df = pd.read_csv(StringIO(content_bytes.decode("latin1")), sep=sep)
                
            return "expression", self._analyze_expression_matrix(df)
            
        return "unsupported", {"raw_size": len(content_bytes)}

    def _analyze_expression_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Dynamically tracks down columns for LFC, P-values, and Identifiers."""
        cols = {c.lower(): c for c in df.columns}
        
        # Map variants of common bioinformatics column naming styles
        lfc_col = next((cols[k] for k in ['log2foldchange', 'log2fc', 'lfc', 'foldchange', 'logfc'] if k in cols), None)
        p_col = next((cols[k] for k in ['pvalue', 'p.value', 'p_value', 'p-value', 'padj', 'p.adj'] if k in cols), None)
        gene_col = next((cols[k] for k in ['gene', 'symbol', 'id', 'gene_name', 'transcript', 'identifier'] if k in cols), None)
        
        # If no gene column found, treat the index as the identifier
        if not gene_col:
            df['_extracted_gene'] = df.index.astype(str)
            gene_col = '_extracted_gene'
            
        anomalies = []
        if df.isnull().sum().sum() > 0:
            anomalies.append(f"Missing Values Alert: Detected {df.isnull().sum().sum()} empty data cells.")
            
        # If columns match, compute the genuine top features
        if lfc_col and p_col:
            df_clean = df.dropna(subset=[lfc_col, p_col]).copy()
            
            # Filter significantly active markers
            sig_condition = (df_clean[p_col] < 0.05)
            up_regulated = df_clean[sig_condition & (df_clean[lfc_col] > 1)].sort_values(by=lfc_col, ascending=False)
            down_regulated = df_clean[sig_condition & (df_clean[lfc_col] < -1)].sort_values(by=lfc_col, ascending=True)
            
            return {
                "mapped": True,
                "dataframe": df,
                "lfc_col": lfc_col,
                "p_col": p_col,
                "gene_col": gene_col,
                "top_up": up_regulated[[gene_col, lfc_col, p_col]].head(5).to_dict(orient='records'),
                "top_down": down_regulated[[gene_col, lfc_col, p_col]].head(5).to_dict(orient='records'),
                "anomalies": anomalies
            }
            
        return {"mapped": False, "dataframe": df, "anomalies": ["Could not auto-map statistical variables (Log2FC/P-value)."]}
