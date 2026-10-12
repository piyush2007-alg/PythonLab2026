"""Modern Web Frontend HTTP Server for Python Code Quality Analyzer."""

import http.server
import json
import mimetypes
import os
import sys
import threading
import urllib.parse
import webbrowser
from typing import Dict, Any, List

from analyzer import (
    analyze_code,
    analyze_file,
    find_python_files,
    generate_markdown_report,
    compute_grade,
    auto_fix_code,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")


class QualityAnalyzerHandler(http.server.BaseHTTPRequestHandler):
    """Custom HTTP request handler serving API and modern static frontend."""

    def log_message(self, format, *args):
        try:
            sys.stderr.write(f"[PyQuality Server] {self.address_string()} - {format % args}\n")
        except Exception:
            pass

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: str, content_type: str = None):
        if not os.path.isfile(file_path):
            self.send_error(404, f"File not found: {os.path.basename(file_path)}")
            return

        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if "text" in content_type else content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Root route -> serve web/index.html
        if path in ("/", "/index.html"):
            self._send_file(os.path.join(WEB_DIR, "index.html"), "text/html")
            return

        # Static web files
        if path.startswith("/web/") or path in ("/style.css", "/app.js"):
            clean_path = path.replace("/web/", "", 1).lstrip("/")
            target = os.path.join(WEB_DIR, clean_path)
            self._send_file(target)
            return

        # API: Starter templates
        if path == "/api/templates":
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
                },
                {
                    "name": "class_template.py",
                    "title": "Class Architecture Template",
                    "code": (
                        '"""Module providing a standard DataProcessor class."""\n\n\n'
                        'class DataProcessor:\n'
                        '    """Encapsulates data cleaning and batch processing."""\n\n'
                        '    def __init__(self, items=None):\n'
                        '        """Initialize with optional items list."""\n'
                        '        self.items = items or []\n\n'
                        '    def process(self):\n'
                        '        """Return non-empty string representations."""\n'
                        '        return [str(item).strip() for item in self.items if item is not None]\n'
                    )
                }
            ]
            self._send_json({"success": True, "templates": templates})
            return

        # API: Read content of any project Python file
        if path == "/api/file-content":
            rel_path = query.get("path", [""])[0]
            if not rel_path or ".." in rel_path:
                self._send_json({"error": "Invalid file path"}, 400)
                return
            full_path = os.path.normpath(os.path.join(BASE_DIR, rel_path))
            if not os.path.isfile(full_path):
                # Fallback: search by basename across project
                base = os.path.basename(rel_path)
                for root, _, files in os.walk(BASE_DIR):
                    if base in files:
                        full_path = os.path.join(root, base)
                        break

            if not os.path.isfile(full_path):
                self._send_json({"error": "File not found"}, 404)
                return

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._send_json({"success": True, "path": rel_path, "content": content})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # API: List workspace Python files
        if path == "/api/workspace-files":
            files = []
            for root, dirs, filenames in os.walk(BASE_DIR):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "web", "sample_inputs")]
                for fn in filenames:
                    if fn.endswith(".py"):
                        rel_path = os.path.relpath(os.path.join(root, fn), BASE_DIR)
                        files.append(rel_path.replace("\\", "/"))
            self._send_json({"success": True, "files": sorted(files)})
            return

        # Try looking in web directory
        static_candidate = os.path.join(WEB_DIR, path.lstrip("/"))
        if os.path.isfile(static_candidate):
            self._send_file(static_candidate)
            return

        self.send_error(404, "Not Found")

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

        # API: Analyze single code snippet
        if path == "/api/analyze":
            code = payload.get("code", "")
            filename = payload.get("filename", "code.py")
            report = analyze_code(code, filename)
            self._send_json({"success": True, "report": report})
            return

        # API: Analyze batch of files passed in payload
        if path == "/api/analyze-files":
            files = payload.get("files", [])
            reports = []
            for item in files:
                fname = item.get("name", "file.py")
                fcode = item.get("content", "")
                reports.append(analyze_code(fcode, fname))

            total = len(reports)
            avg = round(sum(r["score"] for r in reports) / total, 1) if total else 0
            self._send_json({
                "success": True,
                "reports": reports,
                "summary": {
                    "total_files": total,
                    "average_score": avg,
                    "overall_grade": compute_grade(avg),
                    "total_issues": sum(len(r["issues"]) for r in reports),
                    "high_issues": sum(r["stats"]["high"] for r in reports),
                    "medium_issues": sum(r["stats"]["medium"] for r in reports),
                    "low_issues": sum(r["stats"]["low"] for r in reports)
                }
            })
            return

        # API: Analyze workspace project files
        if path == "/api/analyze-workspace":
            rel_dir = payload.get("directory", "")
            target_path = os.path.join(BASE_DIR, rel_dir) if rel_dir else BASE_DIR
            if not os.path.exists(target_path):
                self._send_json({"error": "Path does not exist"}, 404)
                return

            py_files = find_python_files(target_path)
            py_files = [
                f for f in py_files
                if "sample_inputs" not in f
                and "web" not in f
                and not os.path.basename(f).startswith(".")
            ]

            reports = []
            for fpath in py_files:
                rel = os.path.relpath(fpath, BASE_DIR).replace("\\", "/")
                reports.append(analyze_file(fpath))
                reports[-1]["filename"] = rel

            total = len(reports)
            avg = round(sum(r["score"] for r in reports) / total, 1) if total else 0
            self._send_json({
                "success": True,
                "reports": reports,
                "summary": {
                    "total_files": total,
                    "average_score": avg,
                    "overall_grade": compute_grade(avg),
                    "total_issues": sum(len(r["issues"]) for r in reports),
                    "high_issues": sum(r["stats"]["high"] for r in reports),
                    "medium_issues": sum(r["stats"]["medium"] for r in reports),
                    "low_issues": sum(r["stats"]["low"] for r in reports)
                }
            })
            return

        # API: Export reports as markdown
        if path == "/api/export-markdown":
            reports = payload.get("reports", [])
            if not reports:
                self._send_json({"error": "No reports provided"}, 400)
                return
            markdown_content = generate_markdown_report(reports)
            self._send_json({"success": True, "markdown": markdown_content})
            return

        # API: Auto-Fix Engine
        if path == "/api/quick-fix":
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

        self.send_error(404, "API endpoint not found")


def start_server(host: str = "127.0.0.1", port: int = 5000, open_browser: bool = True):
    """Start HTTP server and optionally open browser."""
    mimetypes.init()
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/svg+xml", ".svg")

    server_address = (host, port)
    try:
        httpd = http.server.ThreadingHTTPServer(server_address, QualityAnalyzerHandler)
    except OSError as e:
        if "address already in use" in str(e).lower() or getattr(e, "winerror", None) == 10048:
            port += 1
            server_address = (host, port)
            httpd = http.server.ThreadingHTTPServer(server_address, QualityAnalyzerHandler)
        else:
            raise

    url = f"http://{host}:{port}/"
    print("=" * 65)
    print(" [PyQuality] Python Code Quality & Comment Analyzer")
    print("=" * 65)
    print(f" -> Local Web App: {url}")
    print(f" -> API endpoints: {url}api/analyze, {url}api/quick-fix")
    print(" -> Press Ctrl+C in terminal to stop server.")
    print("=" * 65)

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[PyQuality Server] Stopping server...")
    finally:
        httpd.server_close()
        print("[PyQuality Server] Server stopped.")
