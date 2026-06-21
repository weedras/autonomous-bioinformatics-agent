import os
import json

def generate_report(sra_id, workflow_history, output_dir="output"):
    report_path = os.path.join(output_dir, f"{sra_id}_analysis_report.md")
    
    with open(report_path, "w") as f:
        f.write(f"# Autonomous Bioinformatics Agent Report\n\n")
        f.write(f"**Target:** `{sra_id}`\n\n")
        
        f.write("## Execution History\n\n")
        for item in workflow_history:
            if item.get("status") == "success":
                f.write(f"- :white_check_mark: **{item['step']}**: Completed Successfully\n")
            elif item.get("status") == "failed":
                f.write(f"- :x: **{item['step']}**: Failed\n")
                f.write(f"  - Error Log Snippet: `{item.get('error', '')[:100]}...`\n")
            elif "description" in item:
                f.write(f"- :wrench: **Auto-Fix Applied**: {item['description']}\n")
        
        f.write("\n## Outputs\n\n")
        f.write("The following files were generated:\n")
        vcf_path = os.path.join(output_dir, "calls.vcf")
        bam_path = os.path.join(output_dir, "aln.bam")
        
        if os.path.exists(vcf_path):
            f.write(f"- **VCF File:** `{vcf_path}`\n")
        if os.path.exists(bam_path):
            f.write(f"- **BAM File:** `{bam_path}`\n")
            
    return report_path
