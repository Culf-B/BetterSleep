from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.contentType = "text/html"
            self.path = 'public_test/index.html'
        elif self.path == '/script.js':
            self.contentType = "application/javascript"
            self.path = 'public_test/script.js'
        elif self.path == '/style.css':
            self.contentType = "text/css"
            self.path = 'public_test/style.css'
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

    def do_POST(self):
        # Parse the form data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )

        # Get the form values
        first_name = form.getvalue("first_name")
        last_name = form.getvalue("last_name")

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, ' + first_name.encode() + b' ' + last_name.encode())

httpd = HTTPServer(('', 42069), SimpleHTTPRequestHandler)
httpd.serve_forever()