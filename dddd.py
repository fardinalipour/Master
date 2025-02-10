import pandas as pd
import plotly.graph_objects as go
import logging
import os

# --------------------------------------------------
# Logging setup
# --------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# --------------------------------------------------
# Final category colors 
# --------------------------------------------------
final_category_colors = {
    "Fe": "rgba(111,189,209,0.8)",
    "PP": "rgba(258,210,86,0.8)",
    "HIPS": "rgba(23,77,104,0.8)",
    "PE": "rgba(64,102,86,0.8)",
    "AL": "rgba(241,151,90,0.8)",
    "ABS": "rgba(158,73,15,0.8)"
}

# --------------------------------------------------
# Material series colors 
# --------------------------------------------------
series_colors = {
    "PP": "rgba(258,210,86,0.8)",
    "HIPS": "rgba(0,51,102,0.8)",
    "Fe": "rgba(63,166,194,0.8)",
    "Al": "rgba(241,151,90,0.8)",
    "ABS": "rgba(158,73,15,0.8)",
    "PE": "rgba(64,102,86,0.8)"
}

def load_data(file_path):
    """Reads and processes the Excel file."""
    try:
        dataset = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise

    if 'source' not in dataset.columns or 'target' not in dataset.columns:
        raise ValueError("Dataset must contain 'source' and 'target' columns")

    dataset = dataset[1:].copy()

    if 'series' not in dataset.columns:
        dataset['series'] = "Unknown"

    value_columns = [col for col in dataset.columns if col.startswith('value')]

    scale_factor = 10000
    for col in value_columns:
        dataset[col] = pd.to_numeric(dataset[col], errors='coerce') * scale_factor

    nodes = pd.unique(dataset[['source', 'target']].values.ravel('K')).tolist()
    final_categories_list = list(final_category_colors.keys())

    reordered_final = [t for t in final_categories_list if t in nodes]
    other_nodes = [t for t in nodes if t not in reordered_final]
    final_node_order = reordered_final + other_nodes

    node_map = {name: idx for idx, name in enumerate(final_node_order)}
    dataset['source_index'] = dataset['source'].map(node_map)
    dataset['target_index'] = dataset['target'].map(node_map)

    default_node_color = "rgba(127,127,127,0.8)"
    node_colors = [final_category_colors.get(n, default_node_color) for n in final_node_order]

    return dataset, final_node_order, node_colors, value_columns, final_categories_list, final_category_colors

def create_sankey(dataset, nodes, node_colors, value_columns, final_categories, final_cat_colors):
    """Creates and returns a Sankey diagram."""
    default_link_color = "rgba(200,200,200,0.5)"
    link_colors_frames = {}

    for col in value_columns:
        link_colors = []
        for _, row in dataset.iterrows():
            mat_series = row['series']
            link_colors.append(series_colors.get(mat_series, default_link_color))
        link_colors_frames[col] = link_colors

    frames = []
    for col in value_columns:
        frames.append(
            go.Frame(
                data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=30,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color=node_colors
                    ),
                    link=dict(
                        source=dataset['source_index'],
                        target=dataset['target_index'],
                        value=dataset[col],
                        color=link_colors_frames[col]
                    )
                )],
                name=col
            )
        )

    if not value_columns:
        logger.error("No 'value' columns found.")
        return None

    initial_col = value_columns[0]
    fig = go.Figure(
        data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=30,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=node_colors
            ),
            link=dict(
                source=dataset['source_index'],
                target=dataset['target_index'],
                value=dataset[initial_col],
                color=link_colors_frames[initial_col]
            )
        )],
        frames=frames
    )

    fig.update_layout(
        title_text="Sankey Diagram with Updated Labels",
        font_size=12
    )

    return fig  # Returns the figure instead of showing it
