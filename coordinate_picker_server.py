import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from pathlib import Path


class CoordinatePickerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for coordinate picker interface"""

    coordinates_saved = False
    server_should_stop = False

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Serve the coordinate picker HTML file"""
        if self.path == '/' or self.path == '/index.html':
            try:
                html_path = Path(__file__).parent / 'coordinate_picker.html'
                with open(html_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content.encode('utf-8')))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, 'coordinate_picker.html not found')
        else:
            self.send_error(404, 'File not found')

    def do_POST(self):
        """Handle coordinate submission"""
        if self.path == '/save_coordinates':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))

                # Save coordinates to JSON file
                output_path = Path(__file__).parent / 'coordinates.json'
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Mark as saved
                CoordinatePickerHandler.coordinates_saved = True
                CoordinatePickerHandler.server_should_stop = True

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'status': 'success', 'message': 'Coordinates saved'}
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                self.send_error(500, f'Error saving coordinates: {str(e)}')
        else:
            self.send_error(404, 'Endpoint not found')

    def do_OPTIONS(self):
        """Handle preflight requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def start_coordinate_picker_server(port=8765):
    """
    Start the coordinate picker HTTP server

    Args:
        port: Port number to run the server on (default: 8765)

    Returns:
        tuple: (HTTPServer instance, coordinates dict or None)
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, CoordinatePickerHandler)

    print(f"[Coordinate Picker] Server started on http://localhost:{port}")
    print(f"[Coordinate Picker] Open your browser to: http://localhost:{port}")

    # Run server in a separate thread so we can monitor for shutdown
    def run_server():
        while not CoordinatePickerHandler.server_should_stop:
            httpd.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for coordinates to be saved
    print("[Coordinate Picker] Waiting for coordinate selection...")
    server_thread.join()

    # Load and return the saved coordinates
    if CoordinatePickerHandler.coordinates_saved:
        try:
            coordinates_path = Path(__file__).parent / 'coordinates.json'
            with open(coordinates_path, 'r', encoding='utf-8') as f:
                coordinates_data = json.load(f)
            print(f"[Coordinate Picker] Received {coordinates_data['count']} coordinates")
            return httpd, coordinates_data
        except Exception as e:
            print(f"[Coordinate Picker] Error loading coordinates: {e}")
            return httpd, None
    else:
        print("[Coordinate Picker] No coordinates received")
        return httpd, None


if __name__ == '__main__':
    """Test the server"""
    import webbrowser
    import time

    print("Starting coordinate picker server...")
    print("This will open your browser automatically")

    # Start server in background
    server, coords = start_coordinate_picker_server(port=8765)

    # Open browser
    webbrowser.open('http://localhost:8765')

    if coords:
        print("\nCoordinates received:")
        print(json.dumps(coords, indent=2))
    else:
        print("\nNo coordinates received")

    print("\nServer stopped")
