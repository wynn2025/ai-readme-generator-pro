#!/usr/bin/env python3
"""AI README Generator Pro - Entry Point"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_readme_generator_pro import main
if __name__ == '__main__':
    sys.exit(main() or 0)
