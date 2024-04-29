from server import Server, getLatestData
from time import sleep

# Initialize server object
httpServer = Server()

# Start the server (blocking the proces)
httpServer.serve()

# Main loop main thread
while True:
    print("Latest data: ", getLatestData())
    
    # Delay for server thread to do its tasks
    sleep(1)