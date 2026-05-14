#!/usr/bin/env python3
"""AI README Generator Pro v1.0.0
Scan project source code, analyze structure, generate professional README.md.
Supports Python/Node/Go/Rust/Java/C++. Optional DeepSeek API enhancement.
"""
import os, sys, re, json, argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

VERSION = "1.0.0"
NL = chr(10)
BT = chr(96)
TB = BT * 3
IGNORE = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", ".idea", ".vscode", ".eggs"}
LANG_EXT = {"python": {".py"}, "node": {".js", ".ts"}, "go": {".go"}, "rust": {".rs"}, "java": {".java"}, "cpp": {".cpp", ".hpp", ".h"}}
