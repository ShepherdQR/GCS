import http.server
import socketserver
import webbrowser
import os
import threading


def start_server(directory: str = None, port: int = 8000, open_browser: bool = True):
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

    os.makedirs(directory, exist_ok=True)

    handler = http.server.SimpleHTTPRequestHandler

    class ChdirHandler(handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(("", port), ChdirHandler) as httpd:
        url = f"http://localhost:{port}/index.html"
        print(f"Serving GCS display at {url}")
        print(f"Serving directory: {directory}")
        print("Press Ctrl+C to stop the server")

        if open_browser:
            def open_url():
                webbrowser.open(url)
            threading.Timer(0.5, open_url).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
