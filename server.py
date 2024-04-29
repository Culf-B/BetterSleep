from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading
import cgi
import json

# Load setup data
with open("serverSetup.json", "r") as f:
    setupData = json.load(f)
    PATH = setupData["PATH"]
    PORT = setupData["PORT"]

# Latest alarm and time data
latestData = {
    "morningTime": "--:--",
    "nightTime": "--:--",
    "autoTime": "--:--",
    "manualTime": "--:--",
    "dataChanged": False
}

class Server():
    def __init__(self):
        self.server = ThreadingHTTPServer(('', PORT), SimpleHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def serve(self):
        self.server_thread.start()

class SimpleHandler(BaseHTTPRequestHandler):
    # Handle get request for file
    def do_GET(self):
        self.tempStatus = 200
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
        else:
            self.tempStatus = 404
            self.contentType = "text/html"
            self.path = PATH + '404.html'

        file_to_open = open(self.path).read()
        self.send_response(self.tempStatus)
        self.send_header('Content-type', self.contentType)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    # Handle post with form data
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )
        # Upate data
        latestData["morningTime"] = form.getvalue("mTime")
        latestData["nightTime"] = form.getvalue("aTime")
        latestData["autoTime"] = form.getvalue("autoTime")
        latestData["manualTime"] = form.getvalue("manualTime")
        latestData["dataChanged"] = True

        self.send_response(301)
        self.send_header('Location','/indstillinger')
        self.end_headers()

def getLatestData():
    if latestData["dataChanged"]:
        latestData["dataChanged"] = False
        returnData = latestData.copy()
        returnData["dataChanged"] = True
        return returnData
    else:
        return latestData