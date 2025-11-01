"""
Main entry point for the RAG Agent Platform.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_agent.api_server import main as api_main
from rag_agent.web_ui import main as web_main


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RAG Agent Platform")
    parser.add_argument("command", choices=["api", "web"], help="Command to run")
    parser.add_argument("--config", default="default", help="Configuration name")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    if args.command == "api":
        api_main()
    elif args.command == "web":
        web_main()


if __name__ == "__main__":
    main()
