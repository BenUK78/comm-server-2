import http.server
import socketserver
import ssl
import os
import time
import sys

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Service 2 is talking</h1><p>This is Service 2.  I am responding to a request.</p></body></html>")
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Service 2</h1><p>This is Service 2.</p><p><a href='/test'>Test</a></p></body></html>")

def run_server(port, server_type='http', certfile=None, keyfile=None):
    Handler = MyHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        if server_type == 'https':
            if certfile and keyfile:
                httpd.socket = ssl.wrap_socket(httpd.socket,
                                               certfile=certfile, keyfile=keyfile,
                                               ssl_version=ssl.PROTOCOL_TLS_SERVER)
            else:
                print("Error: certfile and keyfile are required for https")
                return
        print(f"Serving {server_type} at port", port)
        httpd.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002)) # Get port from environment variable, default to 8002
    server_type = 'http' # Crucial: Inside the mesh, use http.  Istio handles TLS.
    certfile = None # Initialize certfile
    keyfile = None # Initialize keyfile
    # certfile = "path/to/your/server2.crt"
    # keyfile = "path/to/your/server2.key"

    if server_type == 'https' and (not os.path.exists(certfile) or not os.path.exists(keyfile)):
        print(f"Error: certfile ({certfile}) or keyfile ({keyfile}) not found.")
        exit(1)

    run_server(port, server_type, certfile, keyfile)