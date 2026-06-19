#!/usr/bin/env python3
"""
Serve ClaimGraph and accept POST /save to write graph.json back to disk.
Run from the ClaimGraph directory:  python serve.py
Then open http://localhost:8080 in your browser.
"""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            with open('graph.json', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress per-request noise

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'ClaimGraph running at http://localhost:{PORT}  (Ctrl-C to stop)')
HTTPServer(('', PORT), Handler).serve_forever()
