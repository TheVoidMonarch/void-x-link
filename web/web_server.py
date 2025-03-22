#!/usr/bin/env python3
"""
VoidLink Web Server

A simple HTTP server to serve the VoidLink web interface.
"""

import os
import sys
import json
import mimetypes
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import VoidLink modules
try:
    import authentication
    import file_transfer
    import file_security
    VOIDLINK_MODULES_LOADED = True
except ImportError:
    print("Warning: VoidLink modules could not be imported. Running in demo mode.")
    VOIDLINK_MODULES_LOADED = False

# Constants
PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

class VoidLinkRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for VoidLink web server"""
    
    def __init__(self, *args, **kwargs):
        self.directory = WEB_DIR
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_request(path, parsed_url)
            return
        
        # Serve index.html for root path
        if path == '/':
            self.path = '/index.html'
        
        # Serve static files
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API endpoints
        if path.startswith('/api/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                self.handle_api_post_request(path, json_data)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON data")
            
            return
        
        # Not found
        self.send_error(404, "Not found")
    
    def handle_api_request(self, path, parsed_url):
        """Handle API GET requests"""
        query = parse_qs(parsed_url.query)
        
        if path == '/api/files':
            self.handle_files_request(query)
        elif path == '/api/user':
            self.handle_user_request(query)
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_api_post_request(self, path, json_data):
        """Handle API POST requests"""
        if path == '/api/login':
            self.handle_login_request(json_data)
        elif path == '/api/upload':
            self.handle_upload_request(json_data)
        elif path == '/api/share':
            self.handle_share_request(json_data)
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_files_request(self, query):
        """Handle files API request"""
        # In a real implementation, this would fetch files from the database
        # For demo purposes, we'll return mock data
        
        files = [
            {
                "id": "file1",
                "name": "Project_Proposal.pdf",
                "type": "pdf",
                "size": 1258291,
                "modified": "2023-03-15T14:30:00Z",
                "uploader": "john.doe"
            },
            {
                "id": "file2",
                "name": "Vacation_Photo.jpg",
                "type": "image",
                "size": 3672144,
                "modified": "2023-03-14T10:15:00Z",
                "uploader": "john.doe"
            },
            {
                "id": "file3",
                "name": "Meeting_Notes.docx",
                "type": "doc",
                "size": 251432,
                "modified": "2023-03-12T09:45:00Z",
                "uploader": "john.doe"
            },
            {
                "id": "file4",
                "name": "Budget_2023.xlsx",
                "type": "spreadsheet",
                "size": 1887432,
                "modified": "2023-03-08T16:20:00Z",
                "uploader": "john.doe"
            }
        ]
        
        self.send_json_response(200, files)
    
    def handle_user_request(self, query):
        """Handle user API request"""
        # In a real implementation, this would fetch user data from the database
        # For demo purposes, we'll return mock data
        
        user = {
            "username": "john.doe",
            "displayName": "John Doe",
            "email": "john.doe@example.com",
            "role": "premium",
            "storage": {
                "used": 6.5 * 1024 * 1024 * 1024,  # 6.5 GB in bytes
                "total": 10 * 1024 * 1024 * 1024,  # 10 GB in bytes
                "breakdown": {
                    "documents": 2.1 * 1024 * 1024 * 1024,
                    "images": 1.8 * 1024 * 1024 * 1024,
                    "videos": 1.5 * 1024 * 1024 * 1024,
                    "other": 1.1 * 1024 * 1024 * 1024
                }
            }
        }
        
        self.send_json_response(200, user)
    
    def handle_login_request(self, json_data):
        """Handle login API request"""
        username = json_data.get('username')
        password = json_data.get('password')
        
        if not username or not password:
            self.send_json_response(400, {"error": "Username and password are required"})
            return
        
        # In a real implementation, this would authenticate the user
        # For demo purposes, we'll accept any login
        
        if VOIDLINK_MODULES_LOADED:
            try:
                # Use the actual authentication module
                success = authentication.authenticate_user(username, password)
                if success:
                    self.send_json_response(200, {"success": True, "message": "Login successful"})
                else:
                    self.send_json_response(401, {"error": "Invalid username or password"})
            except Exception as e:
                self.send_json_response(500, {"error": str(e)})
        else:
            # Demo mode
            if username == "demo" and password == "password":
                self.send_json_response(200, {"success": True, "message": "Login successful"})
            else:
                self.send_json_response(401, {"error": "Invalid username or password"})
    
    def handle_upload_request(self, json_data):
        """Handle upload API request"""
        # In a real implementation, this would handle file uploads
        # For demo purposes, we'll just acknowledge the request
        
        self.send_json_response(200, {"success": True, "message": "Upload acknowledged"})
    
    def handle_share_request(self, json_data):
        """Handle share API request"""
        file_id = json_data.get('fileId')
        recipient = json_data.get('recipient')
        
        if not file_id or not recipient:
            self.send_json_response(400, {"error": "File ID and recipient are required"})
            return
        
        # In a real implementation, this would share the file with the recipient
        # For demo purposes, we'll just acknowledge the request
        
        self.send_json_response(200, {
            "success": True,
            "message": f"File shared with {recipient}",
            "shareLink": f"https://voidlink.example.com/share/{file_id}"
        })
    
    def send_json_response(self, status_code, data):
        """Send a JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server():
    """Run the web server"""
    handler = VoidLinkRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"VoidLink Web Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")


if __name__ == "__main__":
    # Ensure the web directory exists
    if not os.path.exists(WEB_DIR):
        print(f"Error: Web directory not found: {WEB_DIR}")
        sys.exit(1)
    
    # Run the server
    run_server()