from server import Server, getLatestData
from time import sleep

# Initialize server object
httpServer = Server()

# Start the server (blocking the proces)
httpServer.serve()

# Main loop main thread
while True:
    
    # Listen for button / switch inputs

    # Log phone status

    # Listen for network changes if hotspot has been turned on


    # if hotspot turned on???:

    settingData = getLatestData()
    # Update settings if data has been changed
    if settingData["dataChanged"]:
        # Update alarm times


        # Update rtc time (or just time settings if it is too hard to implement rtc)

        pass

    # Update alarm status (there should be an alarm class keeping track of every alarm)

    

    # Update display



    # Delay for server thread to do its tasks (delay might have to be lower myb .1 for button to work)
    sleep(1)