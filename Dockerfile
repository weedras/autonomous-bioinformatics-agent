# Use Miniconda as the base image for easy bioinformatics software installation
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /app

# Install basic linux dependencies
RUN apt-get update && apt-get install -y wget curl

# Install bioinformatics tools using Conda (Bioconda channel)
RUN conda install -y -c bioconda bwa-mem2 samtools bcftools sra-tools fastqc fastp

# Install python dependencies for LLM integration and Web UI
RUN pip install google-generativeai streamlit

# Copy the agent's Python code into the container
COPY app.py agent.py workflow.py executor.py healer.py reporter.py uploader.py ./

# Make output directory
RUN mkdir -p output

# Expose Streamlit port
EXPOSE 8501

# Set the default command to run the web dashboard
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
