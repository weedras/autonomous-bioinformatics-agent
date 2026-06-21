# Use Miniconda as the base image for easy bioinformatics software installation
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /app

# Install basic linux dependencies
RUN apt-get update && apt-get install -y wget curl

# Install bioinformatics tools using Conda (Bioconda channel)
RUN conda install -y -c bioconda bwa-mem2 samtools bcftools sra-tools

# Copy the agent's Python code into the container
COPY agent.py workflow.py executor.py healer.py reporter.py uploader.py ./

# Make output directory
RUN mkdir -p output

# Set the default command to run the agent
ENTRYPOINT ["python3", "agent.py"]
