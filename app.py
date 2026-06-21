import streamlit as st
import logging
import os
import sys
from workflow import GenomicWorkflow
from reporter import generate_report

st.set_page_config(page_title="Autonomous Bioinformatics Agent", page_icon="🧬", layout="wide")

# Custom Logging Handler to stream logs to Streamlit
class StreamlitHandler(logging.Handler):
    def __init__(self, st_container):
        super().__init__()
        self.st_container = st_container
        self.logs = []

    def emit(self, record):
        msg = self.format(record)
        self.logs.append(msg)
        # Display the latest 20 lines to keep UI responsive
        display_text = "\n".join(self.logs[-20:])
        self.st_container.code(display_text, language="bash")

st.title("🧬 Autonomous Bioinformatics Agent")
st.markdown("Run automated variant calling pipelines that self-heal from tool crashes using LLMs.")

# Sidebar for inputs
with st.sidebar:
    st.header("Pipeline Configuration")
    sra_id = st.text_input("SRA Run ID", value="SRR390728")
    ref_path = st.text_input("Reference FASTA Path", value="phix.fasta")
    api_key = st.text_input("Gemini API Key (Optional)", type="password")
    outdir = st.text_input("Output Directory", value="output")
    
    start_run = st.button("🚀 Start Analysis", type="primary")

# Main execution area
if start_run:
    if not sra_id or not ref_path:
        st.error("Please provide both SRA ID and Reference FASTA path.")
    else:
        st.info("Pipeline started. Monitoring logs...")
        
        # Set API Key
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            
        # Create UI container for logs
        log_container = st.empty()
        
        # Setup logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Clear existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()
            
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add stdout handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # Add Streamlit handler
        sl_handler = StreamlitHandler(log_container)
        sl_handler.setFormatter(formatter)
        logger.addHandler(sl_handler)
        
        # Execute workflow
        with st.spinner("Pipeline is running... Please wait."):
            try:
                workflow = GenomicWorkflow(sra_id, ref_path, outdir)
                success = workflow.run()
                
                if success:
                    st.success("🎉 Pipeline executed successfully!")
                else:
                    st.error("❌ Pipeline failed even after attempted auto-healing.")
                
                # Generate Report
                st.markdown("### Execution Report")
                report_path = generate_report(sra_id, workflow.history, outdir)
                
                # Read and display report
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_content = f.read()
                    st.markdown(report_content)
                
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
