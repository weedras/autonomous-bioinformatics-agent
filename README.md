# Autonomous Bioinformatics Agent

An AI-driven Python agent that autonomously executes genomic analysis pipelines, monitors execution logs, diagnoses failures, applies corrective actions, and generates final variant-calling results.

## Features
- **Auto-Healing**: Parses `stderr` of crashed bioinformatics tools and automatically executes recovery commands (e.g., generating missing indices).
- **Automated Workflow**: Downloads sequencing reads, aligns using `bwa-mem2`, sorts and indexes with `samtools`, and calls variants with `bcftools`.
- **Detailed Reporting**: Generates a final Markdown summary report.

## Running with Docker (Recommended)

The easiest way to run the agent is using Docker. The Docker container comes pre-packaged with all the required bioinformatics tools (`bwa-mem2`, `samtools`, `bcftools`, `wget`).

1. **Build the Docker Image**:
   ```bash
   docker build -t autonomous-bio-agent .
   ```

2. **Run the Dashboard**:
   ```bash
   docker run -p 8501:8501 -v $(pwd)/output:/app/output autonomous-bio-agent
   ```
   *(Note: You must map your data and references into the container or download them directly within the UI if supported).*

3. **Access the UI**:
   Open your browser and navigate to [http://localhost:8501](http://localhost:8501)

## Running Locally

To run the web dashboard locally, you need Python 3 installed alongside the bioinformatics toolchain:
- `bwa-mem2`
- `samtools`
- `bcftools`
- `fastqc`
- `fastp`
- `streamlit`

```bash
streamlit run app.py
```
