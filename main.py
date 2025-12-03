#!/usr/bin/env python3
"""
Main Entry Point for Automated Insight Engine
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from src.api import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting Automated Insight Engine...")
    
    # Create Flask app
    config = {
        'upload_folder': './uploads',
        'output_folder': './output'
    }
    
    app = create_app(config)
    
    # Run development server
    logger.info("Server starting on http://0.0.0.0:5000")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )


if __name__ == '__main__':
    main()
