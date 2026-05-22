import streamlit as st
import pandas as pd
from src.orchestrator import ProcessOrchestrator
from src.visualizer import create_volcano_plot

st.set_page_config(page_title="BioScientist AI", page_icon="🧬", layout="wide")

# Initialize state
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.results = {}

st.title("🧬 AI Bioinformatics Research Assistant")
st.markdown("Upload Fasta, BAM, VCF, CSV, or PDFs. The AI will auto-detect, analyze, and explain your results.")

# 1. File Upload
uploaded_files = st.file_uploader(
    "Drop biological data files here", 
    accept_multiple_files=True,
    type=["fasta", "fa", "fastq", "bam", "vcf", "csv", "pdf", "txt"]
)

if uploaded_files and not st.session_state.analysis_complete:
    if st.button("Run AI Analysis", type="primary"):
        with st.status("Initializing AI Research Pipeline...", expanded=True) as status:
            orchestrator = ProcessOrchestrator()
            
            st.write("📂 Identifying file types and extracting metadata...")
            parsed_data = orchestrator.parse_files(uploaded_files)
            
            st.write("🧠 Running statistical analysis and anomaly detection...")
            stats_results = orchestrator.analyze_data(parsed_data)
            
            st.write("🔬 Generating biological explanations and finding literature...")
            final_report = orchestrator.generate_explanation(stats_results)
            
            st.session_state.results = final_report
            st.session_state.analysis_complete = True
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            st.rerun()

# 2. Results Dashboard
if st.session_state.analysis_complete:
    res = st.session_state.results
    
    # Top-level summary
    st.header("Executive Summary")
    st.info(res.get("summary", "No summary generated."))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Visualizations")
        # Example: Render Volcano plot if we have differential expression data
        if "diff_expr" in res:
            fig = create_volcano_plot(res["diff_expr"])
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("Data Quality & Anomalies")
        if res.get("anomalies"):
            for anomaly in res["anomalies"]:
                st.warning(anomaly)
        else:
            st.success("Sequencing QC passed. No major anomalies detected.")
            
    st.divider()
    
    # The "Explain My Results" Feature
    st.header("Explain My Results")
    st.markdown(res.get("detailed_explanation", ""))
    
    st.subheader("Suggested Next Experiments")
    for exp in res.get("next_steps", []):
        st.markdown(f"- {exp}")
        
    st.subheader("Literature Citations")
    for cite in res.get("citations", []):
        st.markdown(f"📖 {cite}")
        
    if st.button("Reset Analysis"):
        st.session_state.analysis_complete = False
        st.session_state.results = {}
        st.rerun()