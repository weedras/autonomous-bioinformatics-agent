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

2. **Run the Agent**:
   ```bash
   docker run -it -v $(pwd)/output:/app/output autonomous-bio-agent --sra SRR390728 --ref path/to/your/reference.fasta
   ```
   *(Note: You must mount your reference genome into the container or provide a network link to download it).*

## Running Locally

To run locally, you need Python 3 installed alongside the bioinformatics toolchain:
- `bwa-mem2`
- `samtools`
- `bcftools`

```bash
python3 agent.py --sra SRR390728 --ref phix.fasta
```
