#!/usr/bin/env python3
"""
OpenClaw Paper Questions Skill - Main Execution Script
This script handles the OpenClaw skill execution for paper questions generation.
"""

import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_recommended_questions import main as paper_questions_main


def main():
    """Main entry point for OpenClaw paper-questions skill"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Paper Questions Skill - Extracts text from PDF files and generates 3 recommended questions"
    )
    
    parser.add_argument("pdf_path", help="Path to the PDF file to generate questions for")
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the generated questions prompt"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        return 1
    
    try:
        result = paper_questions_main(args.pdf_path, None, args.output)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
