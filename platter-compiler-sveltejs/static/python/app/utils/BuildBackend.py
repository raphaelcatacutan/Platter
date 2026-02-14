"""
This should run all automation process to build the backend.
Insert more automations in the futures so we don't have a 
lot of files and automation and configurations. 
"""

from app.utils.FormatParser import main as format_parser

if __name__ == "__main__":
    format_parser()