"""Application entrypoint for Python Code Quality Analyzer Web Interface.

Run with:
    python app.py
or:
    python app.py 8000
"""

import sys
from server import start_server

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port=port)
