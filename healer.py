import re
import logging
import os
import json
import google.generativeai as genai
from executor import ExecutionError

logger = logging.getLogger('healer')

class Healer:
    def __init__(self):
        # We will keep a history of attempted fixes to avoid infinite loops
        self.attempted_fixes = []

    def ask_llm_for_fix(self, command, stderr, context):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for fast and cost-effective JSON parsing
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are an expert Bioinformatics AI Agent.
A pipeline command failed. Diagnose the error from the stderr log.
If the error is recoverable (e.g. missing index, missing directory, incorrect permissions), provide a bash command to fix it.
If the error is unrecoverable (e.g. missing software that cannot be installed, corrupted raw data), set status to "unrecoverable".

Command that failed:
{command}

Stderr:
{stderr}

Context:
{json.dumps(context)}

Respond strictly in JSON format matching this schema:
{{
  "status": "recoverable" or "unrecoverable",
  "action": "run_command",
  "command": "the bash command to run to fix the issue",
  "description": "brief description of the fix",
  "reason": "if unrecoverable, why"
}}
"""
        try:
            # We enforce JSON output 
            response = model.generate_content(
                prompt, 
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            result = json.loads(response.text)
            return result
        except Exception as e:
            logger.error(f"LLM API Call failed: {e}")
            return None

    def diagnose_and_fix(self, error: ExecutionError, context: dict):
        """
        Analyzes the ExecutionError and returns a corrective action.
        """
        stderr = error.stderr.lower()
        command = error.command
        
        logger.info(f"Diagnosing error for command: {command}")
        
        # 1. Try LLM first if API key is present
        if os.environ.get("GEMINI_API_KEY"):
            logger.info("Asking Gemini LLM for a dynamic fix...")
            fix_action = self.ask_llm_for_fix(command, error.stderr, context)
            if fix_action and fix_action.get("status") == "recoverable":
                fix_cmd = fix_action.get("command")
                if fix_cmd in self.attempted_fixes:
                    return {"status": "unrecoverable", "reason": "LLM suggested a fix that was already attempted."}
                
                logger.warning(f"LLM Diagnosis: {fix_action.get('description')}")
                self.attempted_fixes.append(fix_cmd)
                return fix_action
            elif fix_action and fix_action.get("status") == "unrecoverable":
                logger.error(f"LLM determined error is unrecoverable: {fix_action.get('reason')}")
                return fix_action
            else:
                logger.warning("LLM failed to provide a valid fix. Falling back to hardcoded rules.")
        
        # 2. Hardcoded Fallbacks
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
            if fix_action["command"] in self.attempted_fixes:
                return {"status": "unrecoverable", "reason": "Already attempted to build index and it failed again."}
            
            self.attempted_fixes.append(fix_action["command"])
            return fix_action
            
        logger.error("Could not diagnose the error automatically.")
        return {"status": "unrecoverable", "reason": "Unknown error pattern."}
