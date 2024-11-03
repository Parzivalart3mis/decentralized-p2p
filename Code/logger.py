import logging
import os
from datetime import datetime

def setup_logger(peer_id):
    """Setup logger with a unique log file per node based on peer_id."""
    log_dir = "Out/Logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate a unique log file name for each node
    log_filename = f"{log_dir}/node_{peer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure logging
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_filename
