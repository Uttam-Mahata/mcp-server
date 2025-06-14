#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_gemini_mcp import main

if __name__ == "__main__":
    asyncio.run(main())
