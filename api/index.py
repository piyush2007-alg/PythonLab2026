"""Vercel Serverless Function entrypoint for Python Code Quality Analyzer.

Exposes REST API endpoints on Vercel:
- POST /api/analyze
- POST /api/quick-fix
- POST /api/export-markdown
- GET  /api/templates
- GET  /api/health
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import urllib.parse

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analyzer import (
    analyze_code,
    auto_fix_code,
    generate_markdown_report,
    compute_grade,
)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless request handler."""

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/api/health", "/api/health/"):
            self._send_json({"status": "ok", "platform": "vercel", "engine": "AST 2.0"})
            return

        if path in ("/api/templates", "/api/templates/"):
            templates = [
                {
                    "name": "starter.py",
                    "title": "Clean Starter Template",
                    "code": (
                        '"""A clean, well-documented Python module."""\n\n\n'
                        'def calculate_summary(numbers):\n'
                        '    """Calculate and return the average and total of numbers."""\n'
                        '    if not numbers:\n'
                        '        return {"total": 0, "average": 0.0}\n'
                        '    total = sum(numbers)\n'
                        '    average = total / len(numbers)\n'
                        '    return {"total": total, "average": round(average, 2)}\n'
                    )
                }
            ]
            self._send_json({"success": True, "templates": templates})
            return

        self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception as e:
            self._send_json({"error": f"Invalid JSON payload: {str(e)}"}, 400)
            return

        # POST /api/analyze
        if path.endswith("/analyze") or path == "/api/analyze":
            code = payload.get("code", "")
            filename = payload.get("filename", "code.py")
            report = analyze_code(code, filename)
            self._send_json({"success": True, "report": report})
            return

        # POST /api/quick-fix
        if path.endswith("/quick-fix") or path == "/api/quick-fix":
            code = payload.get("code", "")
            filename = payload.get("filename", "code.py")
            fix_result = auto_fix_code(code, filename)
            self._send_json({
                "success": True,
                "fixed_code": fix_result["fixed_code"],
                "fixes_applied": fix_result["fixes_applied"],
                "fixes_count": fix_result["fixes_count"],
                "score_before": fix_result["score_before"],
                "score_after": fix_result["score_after"],
                "grade_before": fix_result["grade_before"],
                "grade_after": fix_result["grade_after"]
            })
            return

        # POST /api/export-markdown
        if path.endswith("/export-markdown") or path == "/api/export-markdown":
            reports = payload.get("reports", [])
            if not reports:
                self._send_json({"error": "No reports provided"}, 400)
                return
            markdown_content = generate_markdown_report(reports)
            self._send_json({"success": True, "markdown": markdown_content})
            return

        self._send_json({"error": f"Unknown POST route: {path}"}, 404)
