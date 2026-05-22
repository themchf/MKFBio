import plotly.express as px
import pandas as pd
import numpy as np

def create_volcano_plot(df: pd.DataFrame):
    """
    Expects a DataFrame with 'gene', 'log2FoldChange', and 'pvalue'.
    """
    # If using mock data (since we don't have a real CSV uploaded yet)
    if not isinstance(df, pd.DataFrame) or 'pvalue' not in df.columns:
        # Generate mock data for the UI
        np.random.seed(42)
        df = pd.DataFrame({
            'gene': [f'GENE_{i}' for i in range(1, 501)],
            'log2FoldChange': np.random.normal(0, 2, 500),
            'pvalue': np.random.uniform(0, 0.05, 500)
        })
    
    # Calculate -log10(p-value) for the Y axis
    df['-log10(pvalue)'] = -np.log10(df['pvalue'])
    
    # Determine significance thresholds
    df['Significance'] = 'Not Significant'
    df.loc[(df['log2FoldChange'] > 1) & (df['pvalue'] < 0.05), 'Significance'] = 'Upregulated'
    df.loc[(df['log2FoldChange'] < -1) & (df['pvalue'] < 0.05), 'Significance'] = 'Downregulated'

    color_map = {
        'Not Significant': 'grey',
        'Upregulated': 'red',
        'Downregulated': 'blue'
    }

    fig = px.scatter(
        df, 
        x='log2FoldChange', 
        y='-log10(pvalue)',
        color='Significance',
        color_discrete_map=color_map,
        hover_name='gene',
        title='Volcano Plot (Differential Expression)',
        labels={'log2FoldChange': 'Log2 Fold Change', '-log10(pvalue)': '-Log10 P-value'}
    )
    
    # Add threshold lines
    fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="black", annotation_text="p=0.05")
    fig.add_vline(x=1, line_dash="dash", line_color="black")
    fig.add_vline(x=-1, line_dash="dash", line_color="black")
    
    return fig