from server import Server, getLatestData
import time
from alarm import Alarm
from lib import lcdInterface
from random import randint

# Initialize server object
httpServer = Server()

# Start the server (blocking the proces)
httpServer.serve()

# Alarm setup
settings = getLatestData() # Get alarm settings loaded by server
alarmSettings = {}
alarms = {}
alarmKeys = ["morningTime", "nightTime"]
for key in alarmKeys:
    if settings[key] != None:
        alarmSettings[key] = settings[key].split(":")
        alarms[key] = Alarm(key, "Light" if key == "nightTime" else "Sound", int(alarmSettings[key][0]), int(alarmSettings[key][1]))
    else:
        alarms[key] = Alarm(key, "Light" if key == "nightTime" else "Sound")

# Notifications (alarms)
notifQueue = []
notifGoing = False

# Devices setup

# Display color
defaultColor = [255, 255, 255]
flashColors = [[255, 0, 0], [255, 255, 255], [0, 0, 0]]
flashColorIndex = 0
lcdInterface.setRGB(defaultColor[0], defaultColor[1], defaultColor[2])

# Main loop main thread
while True:
    # Listen for switch inputs

    # Log phone status

    # Listen for network changes if hotspot has been turned on


    # if hotspot turned on???:

    settingData = getLatestData()
    # Update settings if data has been changed
    if settingData["dataChanged"]:
        # Update alarm times
        for key in alarmKeys:
            if settings[key] != None:
                alarmSettings[key] = settings[key].split(":")
                alarms[key].setTime(int(alarmSettings[key][0]), int(alarmSettings[key][1]))
            else:
                alarms[key].setTime()

        # Update rtc time (or just time settings if it is too hard to implement rtc)

        pass

    # Update alarm status (there should be an alarm class keeping track of every alarm)
    currentTime = time.localtime()
    for alarm in alarms.values():
        if alarm.checkRing(int(time.strftime("%H", currentTime)), int(time.strftime("%M", currentTime))):
            notifQueue.append(alarm)

    # Update notification
    if len(notifQueue) > 0:
        notifGoing = True

        # Display notification on display

        # Choose how to notify
        if notifQueue[0].notifStyle == "Light": # Flash display backlight
            lcdInterface.setRGB(flashColors[flashColorIndex][0], flashColors[flashColorIndex][1], flashColors[flashColorIndex][2])
            flashColorIndex += 1
            if flashColorIndex >= len(flashColors):
                flashColorIndex = 0

        elif notifQueue[0].notifStyle == "Sound": # Beep the beeper
            pass

        if False: # Check if dismiss button is pressed
            del notifQueue[0] # Delete the notification from the queue
    else:
        notifGoing = False

    # Update display
    if not notifGoing:
        pass # Display time and some icons

    # Delay for server thread to do its tasks (delay might have to be lower myb .1 for button to work)
    time.sleep(0.1)
