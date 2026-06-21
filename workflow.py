import os
import logging
from executor import run_command, ExecutionError
from healer import Healer

logger = logging.getLogger('workflow')

class GenomicWorkflow:
    def __init__(self, sra_id, reference_path, output_dir="output"):
        self.sra_id = sra_id
        self.reference_path = os.path.abspath(reference_path)
        self.output_dir = os.path.abspath(output_dir)
        self.context = {
            "reference_path": self.reference_path,
            "threads": 4
        }
        self.healer = Healer()
        self.history = []

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def execute_with_healing(self, command, step_name):
        """Executes a command and attempts to heal if it fails."""
        max_retries = 3
        attempts = 0

        while attempts < max_retries:
            try:
                logger.info(f"--- Starting Step: {step_name} (Attempt {attempts + 1}) ---")
                stdout, stderr = run_command(command, cwd=self.output_dir)
                self.history.append({"step": step_name, "status": "success", "command": command})
                return True
            except ExecutionError as e:
                logger.error(f"Step '{step_name}' failed.")
                self.history.append({"step": step_name, "status": "failed", "error": e.stderr})
                
                # Attempt to diagnose and fix
                fix = self.healer.diagnose_and_fix(e, self.context)
                
                if fix["status"] == "recoverable":
                    logger.info(f"Applying fix: {fix['description']}")
                    self.history.append({"step": "Auto-Fix", "description": fix['description']})
                    
                    if fix["action"] == "run_command":
                        # Run the fix command (e.g. bwa index)
                        try:
                            # Run the fix command in the same directory as the reference if it's indexing
                            # but for simplicity we run it with absolute paths
                            run_command(fix["command"])
                        except ExecutionError as fix_error:
                            logger.error(f"The fix command failed: {fix_error.stderr}")
                            return False
                    elif fix["action"] == "retry_with_new_context":
                        # Update context and recreate command if needed
                        self.context = fix["context"]
                        # We would need to dynamically regenerate the command if threads changed.
                        # For now, we will handle this via string replacement if threads are in the command.
                        # This is a bit hacky but works for the MVP.
                        if " -t " in command:
                            import re
                            command = re.sub(r'-t \d+', f"-t {self.context['threads']}", command)
                            
                    attempts += 1
                else:
                    logger.error(f"Unrecoverable error: {fix['reason']}")
                    return False
        
        logger.error(f"Max retries reached for step '{step_name}'.")
        return False

    def run(self):
        logger.info(f"Starting workflow for {self.sra_id}")
        
        # 1. Download Reads
        # We download directly from ENA (European Nucleotide Archive) for faster, more reliable downloads
        sra_prefix = self.sra_id[:6]
        url1 = f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{sra_prefix}/{self.sra_id}/{self.sra_id}_1.fastq.gz"
        url2 = f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{sra_prefix}/{self.sra_id}/{self.sra_id}_2.fastq.gz"
        
        dl_cmd = f"wget -q {url1} && wget -q {url2} && gunzip -f {self.sra_id}_1.fastq.gz && gunzip -f {self.sra_id}_2.fastq.gz"
        if not self.execute_with_healing(dl_cmd, "Download Reads"): return False
        
        r1 = f"{self.sra_id}_1.fastq"
        r2 = f"{self.sra_id}_2.fastq"
        
        # 2. Alignment
        # Using bwa-mem2
        aln_cmd = f"bwa-mem2 mem -t {self.context['threads']} \"{self.reference_path}\" \"{r1}\" \"{r2}\" > aln.sam"
        if not self.execute_with_healing(aln_cmd, "Alignment"): return False
        
        # 3. Sorting & Indexing
        sort_cmd = f"samtools sort -@ {self.context['threads']} aln.sam -o aln.bam"
        if not self.execute_with_healing(sort_cmd, "Sorting BAM"): return False
        
        index_cmd = f"samtools index aln.bam"
        if not self.execute_with_healing(index_cmd, "Indexing BAM"): return False
        
        # 4. Variant Calling
        vcf_cmd = f"bcftools mpileup -Ou -f \"{self.reference_path}\" aln.bam | bcftools call -mv -Ov -o calls.vcf"
        if not self.execute_with_healing(vcf_cmd, "Variant Calling"): return False
        
        logger.info("Workflow completed successfully!")
        return True
