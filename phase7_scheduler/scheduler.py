import os
import subprocess
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

# Setup enhanced logging
log_dir = os.path.dirname(os.path.abspath(__file__))
# Configure logging to write to both console and a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'scheduler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Base project directory
PROJECT_ROOT = os.path.abspath(os.path.join(log_dir, '..'))

def run_script(script_path, working_dir):
    """
    Subprocesses a Python script securely and captures output.
    Returns True if the script exited with a 0 return code, False otherwsie.
    """
    logger.info(f"Starting script execution: {script_path}")
    try:
        # Run process and capture output
        result = subprocess.run(
            ['python', script_path],
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Successfully completed: {script_path}")
        logger.debug(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Script failed: {script_path}")
        logger.error(f"Error Code: {e.returncode}")
        logger.error(f"Error Output:\n{e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running {script_path}: {str(e)}")
        return False

def update_pipeline():
    """
    The orchestrator function. Executes Phase 1 first. If successful, triggers Phase 2.
    """
    logger.info("=== Starting Automated RAG Pipeline Update ===")
    
    # 1. Phase 1: Data Acquisition
    phase1_dir = os.path.join(PROJECT_ROOT, 'phase1_data_acquisition')
    scrape_script = os.path.join(phase1_dir, 'scrape_funds.py')
    
    logger.info("Executing Phase 1: Data Acquisition...")
    if not run_script(scrape_script, phase1_dir):
        logger.error("Pipeline aborted: Phase 1 Data Acquisition failed.")
        return
        
    # 2. Phase 2: Indexing / Vector DB
    phase2_dir = os.path.join(PROJECT_ROOT, 'phase2_knowledge_base')
    index_script = os.path.join(phase2_dir, 'ingest_data_faiss.py')
    
    logger.info("Executing Phase 2: Vector DB Indexing...")
    if not run_script(index_script, phase2_dir):
        logger.error("Pipeline aborted: Phase 2 Indexing failed.")
        return
        
    logger.info("=== Automated Update Pipeline Completed Successfully ===")

if __name__ == "__main__":
    logger.info("Executing GitHub Actions Automated Update Runner...")
    try:
        # Trigger the pipeline once instead of waiting in a loop
        update_pipeline()
    except Exception as e:
        logger.error(f"Failed to execute pipeline: {e}")
        exit(1)
