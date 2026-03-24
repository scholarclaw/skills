#!/usr/bin/env python3
"""
OpenClaw Paper Search Skill - Main Execution Script
This script handles the OpenClaw skill execution for paper search functionality.
"""

import argparse
import sys
import os

# Add the skill directory to Python path for module resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_search import main as paper_search_main


def main():
    """Main entry point for OpenClaw paper-search skill"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Paper Search Skill - Searches academic papers using scholar.club API with query keywords"
    )
    
    parser.add_argument("query", help="Search query or keywords")
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the search results"
    )
    parser.add_argument(
        "-r", "--raw", 
        action="store_true",
        help="Output raw API response instead of formatted results"
    )

    
    args = parser.parse_args()
    
    try:
        # Call the main paper search function
        result = paper_search_main(args.query, args.output, args.raw)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
