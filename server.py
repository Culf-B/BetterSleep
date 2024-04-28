from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import json

# Load setup data
with open("serverSetup.json", "r") as f:
    setupData = json.load(f)
    PATH = setupData["PATH"]
    PORT = setupData["PORT"]

class Server():
    def serve(self):
        self.server = HTTPServer(('', PORT), SimpleHandler)
        self.server.serve_forever()

class SimpleHandler(BaseHTTPRequestHandler):
    # Handle get request for file
    def do_GET(self):
        # Files being served
        if self.path == '/':
            self.contentType = "text/html"
            self.path = PATH + 'index.html'
        elif self.path == '/statistik':
            self.contentType = "text/html"
            self.path = PATH + 'statistik.html'
        elif self.path == '/indstillinger':
            self.contentType = "text/html"
            self.path = PATH + 'indstillinger.html'
        elif self.path == '/indstillinger.js':
            self.contentType = "application/javascript"
            self.path = PATH + 'indstillinger.js'
        elif self.path == '/style.css':
            self.contentType = "text/css"
            self.path = PATH + 'style.css'
        # Respond with file if it exists and with a 404 if it does not exist
        try:
            file_to_open = open(self.path).read()
            self.send_response(200)
            self.send_header('Content-type', self.contentType)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        except:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

    # Handle post with form data
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )
        print("Post request: " + form)
        self.send_response(301)
        self.send_header('Location','/indstillinger')
        self.end_headers()