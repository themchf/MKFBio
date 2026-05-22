import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_volcano_plot(analysis_meta: dict) -> go.Figure:
    """Generates an explicit Volcano interactive graph mapping exact user parameters."""
    if not analysis_meta.get("mapped"):
        # Fallback view: Display a generic overview of numerical distributions if columns are unmapped
        df = analysis_meta["dataframe"]
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) >= 2:
            return px.scatter(df, x=num_cols[0], y=num_cols[1], title=f"Feature Distribution: {num_cols[0]} vs {num_cols[1]}")
        
        # Absolute structural fallback
        fig = go.Figure()
        fig.add_annotation(text="Uploaded table structure does not contain statistical identifiers for a Volcano configuration.", showarrow=False)
        return fig

    df = analysis_meta["dataframe"].copy()
    lfc = analysis_meta["lfc_col"]
    p_val = analysis_meta["p_col"]
    gene = analysis_meta["gene_col"]

    # Protect against math logs errors with zero values
    df = df[df[p_val] > 0]
    df['-log10_p'] = -np.log10(df[p_val])

    # Classify each point based on the data
    df['Status'] = 'Not Significant'
    df.loc[(df[lfc] > 1) & (df[p_val] < 0.05), 'Status'] = 'Significantly Upregulated'
    df.loc[(df[lfc] < -1) & (df[p_val] < 0.05), 'Status'] = 'Significantly Downregulated'

    fig = px.scatter(
        df,
        x=lfc,
        y='log10_p',
        color='Status',
        hover_name=gene,
        color_discrete_map={
            'Not Significant': '#bdc3c7',
            'Significantly Upregulated': '#e74c3c',
            'Significantly Downregulated': '#3498db'
        },
        labels={lfc: 'Log2 Fold Change', 'log10_p': '-Log10 (p-value)'},
        title="Interactive Volcanogram"
    )
    
    fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="#2c3e50")
    fig.update_layout(template="plotly_white", legend_title_text="Expression State")
    return fig
