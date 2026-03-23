#!/usr/bin/env python3
"""
OpenClaw Paper Summary Skill - Main Execution Script
This script handles the OpenClaw skill execution for paper summary generation.
"""

import argparse
import sys
import os

# Add the skill directory to Python path for module resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_summary import main as paper_summary_main


def main():
    """Main entry point for OpenClaw paper-summary skill"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Paper Summary Skill - Extracts text from PDF files and generates structured summaries"
    )
    
    parser.add_argument("pdf_path", help="Path to the PDF file to summarize")
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the generated summary prompt"
    )

    
    args = parser.parse_args()
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        return 1
    
    try:
        # Call the main paper summary function
        # We'll need to adapt the paper_summary.py to accept arguments properly
        result = paper_summary_main(args.pdf_path, None, args.output)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
