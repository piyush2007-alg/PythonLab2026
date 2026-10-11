"""Root server entrypoint forwarding to `server` package."""

import sys
from server.http_server import start_server, QualityAnalyzerHandler

__all__ = ["start_server", "QualityAnalyzerHandler"]

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port=port)
