#!/usr/bin/env python3
"""
Serve ClaimGraph and accept POST /save?graph=NAME to write graphs/NAME.json back to disk.
GET /graphs lists available graph names (files in graphs/, without the .json suffix).
Run from the ClaimGraph directory:  python serve.py
Then open http://localhost:8080 in your browser.
"""
import json
import os
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8080
GRAPHS_DIR = 'graphs'
NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path == '/graphs':
            os.makedirs(GRAPHS_DIR, exist_ok=True)
            names = sorted(f[:-5] for f in os.listdir(GRAPHS_DIR) if f.endswith('.json'))
            body = json.dumps(names).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/save':
            name = parse_qs(parsed.query).get('graph', ['main'])[0]
            if not NAME_RE.match(name):
                self.send_response(400)
                self.end_headers()
                return
            os.makedirs(GRAPHS_DIR, exist_ok=True)
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            with open(os.path.join(GRAPHS_DIR, f'{name}.json'), 'wb') as f:
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
