import argparse
import logging
import os
from workflow import GenomicWorkflow
from reporter import generate_report
from uploader import upload_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('agent')

def main():
    parser = argparse.ArgumentParser(description="Autonomous Bioinformatics Agent")
    parser.add_argument("--sra", required=True, help="SRA ID to analyze (e.g., SRR390728)")
    parser.add_argument("--ref", required=True, help="Path to reference FASTA file")
    parser.add_argument("--outdir", default="output", help="Output directory")
    parser.add_argument("--webhook", default="http://localhost:8000/webhook", help="Webhook URL for results")
    
    args = parser.parse_args()
    
    logger.info(f"Received Request: Analyze {args.sra} against {args.ref}")
    
    workflow = GenomicWorkflow(args.sra, args.ref, args.outdir)
    success = workflow.run()
    
    if success:
        logger.info("Pipeline executed successfully. Generating report...")
    else:
        logger.error("Pipeline failed even after attempted auto-healing. Generating error report...")
        
    report_path = generate_report(args.sra, workflow.history, args.outdir)
    vcf_path = os.path.join(args.outdir, "calls.vcf")
    
    upload_success = upload_results(vcf_path, report_path, args.webhook)
    if upload_success:
        logger.info("Results successfully uploaded.")
    else:
        logger.error("Failed to upload results.")

if __name__ == "__main__":
    main()
