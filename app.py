import streamlit as st
import pandas as pd
import os
import time
import shutil
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dddd import load_data, create_sankey  # Import Sankey functions

# Paths
UPLOAD_FOLDER = "uploaded_files"
EXCEL_FILE_PATH = os.path.join(UPLOAD_FOLDER, "data.xlsx")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Watchdog event handler
class ExcelFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == EXCEL_FILE_PATH:
            st.session_state["updated"] = True  # Flag for Streamlit to update

# Start Watchdog observer
def start_watchdog():
    observer = Observer()
    event_handler = ExcelFileHandler()
    observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=False)
    observer.start()
    return observer

# Initialize Streamlit session state
if "updated" not in st.session_state:
    st.session_state["updated"] = False

observer = start_watchdog()

st.title("📊 Auto-Updating Sankey Diagram")

uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    with open(EXCEL_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ File uploaded! Edit in Excel to update.")

if os.path.exists(EXCEL_FILE_PATH) and st.session_state["updated"]:
    try:
        df, nodes, node_colors, value_columns, final_categories, final_category_colors = load_data(EXCEL_FILE_PATH)
        st.write("🔄 **Excel file updated! Reloading data...**")
        fig = create_sankey(df, nodes, node_colors, value_columns, final_categories, final_category_colors)
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"❌ Error: {e}")
    
    st.session_state["updated"] = False
