#!/usr/bin/env python3
import http.server
import socketserver
import os
import urllib.parse

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # If it's a directory or URL without extension
        full_path = os.path.join(DIRECTORY, path.lstrip('/'))
        if os.path.isdir(full_path):
            index_path = os.path.join(full_path, 'index.html')
            if os.path.exists(index_path):
                if not path.endswith('/'):
                    self.send_response(301)
                    new_path = path + '/'
                    if parsed.query:
                        new_path += '?' + parsed.query
                    self.send_header('Location', new_path)
                    self.end_headers()
                    return
        elif not os.path.exists(full_path):
            # Check if adding .html exists
            if os.path.exists(full_path + '.html'):
                self.path = path + '.html'
            # Check if directory with index.html exists
            elif os.path.exists(os.path.join(full_path, 'index.html')):
                self.send_response(301)
                new_path = path + '/'
                if parsed.query:
                    new_path += '?' + parsed.query
                self.send_header('Location', new_path)
                self.end_headers()
                return

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CleanURLHandler) as httpd:
        print(f"[*] Crafted & Cherished local mirror running at http://localhost:{PORT}")
        print(f"[*] Press Ctrl+C to stop.")
        httpd.serve_forever()
