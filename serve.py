#!/usr/bin/env python3
"""
Serve ClaimGraph and accept POST /save?graph=NAME to write graphs/NAME.json back to disk.
GET /graphs lists available graph names (files in graphs/, without the .json suffix).
GET /consolidations reads consolidations.json (created empty if missing).
POST /consolidations overwrites consolidations.json.
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
CONSOLIDATIONS_FILE = 'consolidations.json'
NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/graphs':
            os.makedirs(GRAPHS_DIR, exist_ok=True)
            names = sorted(f[:-5] for f in os.listdir(GRAPHS_DIR) if f.endswith('.json'))
            self._json(200, json.dumps(names).encode())
        elif path == '/consolidations':
            if not os.path.exists(CONSOLIDATIONS_FILE):
                with open(CONSOLIDATIONS_FILE, 'w') as f:
                    f.write('[]\n')
            with open(CONSOLIDATIONS_FILE, 'rb') as f:
                self._json(200, f.read())
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
        elif parsed.path == '/consolidations':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            with open(CONSOLIDATIONS_FILE, 'wb') as f:
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

    def _json(self, status, body_bytes):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body_bytes)

    def log_message(self, format, *args):
        pass  # suppress per-request noise

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'ClaimGraph running at http://localhost:{PORT}  (Ctrl-C to stop)')
HTTPServer(('', PORT), Handler).serve_forever()
