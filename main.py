from server import Server

# Initialize server object
httpServer = Server()

# Start the server (blocking the proces)
httpServer.serve()