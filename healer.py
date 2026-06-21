import re
import logging
from executor import ExecutionError

logger = logging.getLogger('healer')

class Healer:
    def __init__(self):
        # We will keep a history of attempted fixes to avoid infinite loops
        self.attempted_fixes = []

    def diagnose_and_fix(self, error: ExecutionError, context: dict):
        """
        Analyzes the ExecutionError and returns a corrective action.
        context should contain:
        - reference_path: path to the reference fasta
        - threads: current thread count
        - ...
        """
        stderr = error.stderr.lower()
        command = error.command
        
        logger.info(f"Diagnosing error for command: {command}")
        
        # 1. Missing BWA Index
        # BWA-MEM2 often complains about missing files like .bwt.2bit or .pac
        if "unable to open the file" in stderr and (".bwt.2bit" in stderr or ".pac" in stderr or ".ann" in stderr):
            logger.warning("Detected Missing BWA Index.")
            ref_path = context.get('reference_path')
            if not ref_path:
                return {"status": "unrecoverable", "reason": "Reference path not provided in context."}
            
            fix_action = {
                "status": "recoverable",
                "action": "run_command",
                "command": f"bwa-mem2 index \"{ref_path}\"",
                "description": "Generate missing BWA index."
            }
            # Prevent infinite loops
            if fix_action["command"] in self.attempted_fixes:
                return {"status": "unrecoverable", "reason": "Already attempted to build index and it failed again."}
            
            self.attempted_fixes.append(fix_action["command"])
            return fix_action
            
        # 2. Out of Memory (OOM)
        if "out of memory" in stderr or "killed" in stderr or "memoryerror" in stderr:
            logger.warning("Detected Out of Memory error.")
            current_threads = context.get('threads', 4)
            if current_threads <= 1:
                return {"status": "unrecoverable", "reason": "Already at minimum threads, cannot reduce further."}
            
            new_threads = max(1, current_threads // 2)
            context['threads'] = new_threads
            
            fix_action = {
                "status": "recoverable",
                "action": "retry_with_new_context",
                "context": context,
                "description": f"Reduced threads to {new_threads} to save memory."
            }
            return fix_action

        # 3. Command not found
        if "command not found" in stderr:
            logger.warning("Detected missing dependency.")
            return {"status": "unrecoverable", "reason": "Dependency missing. Please install the required tools."}

        # 4. Samtools / Bcftools missing index
        if "could not load index" in stderr:
            # Example for samtools missing index
            logger.warning("Detected missing BAM/VCF index.")
            # For simplicity in MVP, we will try to find the filename and index it
            # This requires parsing the specific error.
            # In a real agent, we might use an LLM here to figure out exactly what to run.
            pass

        logger.error("Could not diagnose the error automatically.")
        return {"status": "unrecoverable", "reason": "Unknown error pattern."}
