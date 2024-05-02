from server import Server, getLatestData
import time
from alarm import Alarm
from lib import lcdInterface, ultrasonicReader
from random import randint
import os
import json
import RPi.GPIO as GPIO
from subprocess import check_output

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

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
offColor = [0, 0, 0]
loadColor = [0, 0, 255]
flashColors = [[255, 0, 0], [255, 255, 255], [0, 0, 0]]
flashColorIndex = 0
lcdInterface.setRGB(loadColor[0], loadColor[1], loadColor[2])

# Display loading screen
lcdInterface.setText("Starter...")

# Distance sensor

#set GPIO Pins
GPIO_TRIGGER = 15
GPIO_ECHO = 24
GPIO_BUTTON = 17
GPIO_SWITCH_1 = 27
GPIO_SWITCH_2 = 22
GPIO_BUZZER = 23

buzzerState = False
switch1state = False
switch2state = False

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Check if calibration file exists and calibrate if it doesn't exsist
if not os.path.isfile("ultrasonicCalibration.json"):
    lcdInterface.setText("Kalibrerer...\nFJERN MOBIL!")
    os.system("python calibrateDistance.py")
# os.system should run on same proces, so calibration should happen before continueing and file should exsist
with open("ultrasonicCalibration.json", "r") as f:
    calibrationReadings = json.load(f)["readings"]
# If the reading is between these two, there is no phone present
noPhone = [min(calibrationReadings), max(calibrationReadings)]
print(noPhone)
ultrasonicAllowedVariation = 0.5

# Interval
ultrasonicInterval = 10 # Seconds between readings
lastReadingTimestamp = 0 # Timestamp (seconds since epoch of last reading)

# Phone data
phonePresent = False
phoneReadingData = []

# Set default rgb color as loading is now done
lcdInterface.setRGB(defaultColor[0], defaultColor[1], defaultColor[2])
lcdInterface.setText("") # Clear display

# Function to update phonedata with a new day
def addDayToData():
    with open("phoneData.json", "r") as f:
        data = json.load(f)
    
    data["days"].append(
        {
            "morningTime": alarmSettings["morningTime"],
            "nightTime": alarmSettings["nightTime"],
            "removed": [],
            "added": []
        }
    )

    with open("phoneData.json", "w") as f:
        json.dump(data, f)

# Get current date
today = time.localtime().tm_mday
addDayToData()

# Main loop main thread
while True:
    # Listen for switch inputs

    # Log phone status
    tempUltrasonicReading = ultrasonicReader.distance(GPIO_TRIGGER, GPIO_ECHO)
    
    if tempUltrasonicReading < noPhone[0] - ultrasonicAllowedVariation or tempUltrasonicReading > noPhone[1] + ultrasonicAllowedVariation:
        if not phonePresent:
            with open("phoneData.json", "r") as f:
                data = json.load(f)
            data["days"][-1]["added"].append(time.strftime("%H:%M", time.localtime()))
            with open("phoneData.json", "w") as f:
                json.dump(data, f)
        phonePresent = True
    else:
        if phonePresent:
            with open("phoneData.json", "r") as f:
                data = json.load(f)
            data["days"][-1]["removed"].append(time.strftime("%H:%M", time.localtime()))
            with open("phoneData.json", "w") as f:
                json.dump(data, f)
        phonePresent = False

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

    # Update alarm status (there should be an alarm class keeping track of every alarm)
    currentTime = time.localtime()
    for alarm in alarms.values():
        if alarm.checkRing(int(time.strftime("%H", currentTime)), int(time.strftime("%M", currentTime))):
            notifQueue.append(alarm)

    # Update notification
    if len(notifQueue) > 0:
        notifGoing = True

        # Display notification on display
        lcdInterface.setText(notifQueue[0].name)

        # Choose how to notify
        if notifQueue[0].notifStyle == "Light": # Flash display backlight
            lcdInterface.setRGB(flashColors[flashColorIndex][0], flashColors[flashColorIndex][1], flashColors[flashColorIndex][2])
            flashColorIndex += 1
            if flashColorIndex >= len(flashColors):
                flashColorIndex = 0

        elif notifQueue[0].notifStyle == "Sound": # Beep the beeper
            if buzzerState == True:
                buzzerState = False
                GPIO.output(GPIO_BUZZER, False)
            else:
                buzzerState = True
                GPIO.output(GPIO_BUZZER, True)

        if not GPIO.input(GPIO_BUTTON): # Check if dismiss button is pressed
            del notifQueue[0] # Delete the notification from the queue
            GPIO.output(GPIO_BUZZER, False)
            buzzerState = False
    else:
        notifGoing = False
        
    # Update display
    if not notifGoing:

        # Determine displayBackground on/off
        switch1pin = GPIO.input(GPIO_SWITCH_1)
        if switch1pin != switch1state:
            switch1state = switch1pin
            if not switch1pin:
                lcdInterface.setRGB(offColor[0], offColor[1], offColor[2])
            else:
                lcdInterface.setRGB(defaultColor[0], defaultColor[1], defaultColor[2])

        phoneText = "Telefon tilstede" if phonePresent else "Telefon mangler"
        switch2pin = GPIO.input(GPIO_SWITCH_2)
        if switch2pin != switch2state:
            switch2state = switch2pin
            if not switch2pin:
                lcdInterface.setText(time.strftime("%H:%M", time.localtime()) + "\n" + phoneText)
            else:
                lcdInterface.setText(str(check_output(['hostname', '-I'])))

        if not switch2pin:
            lcdInterface.setText_norefresh(time.strftime("%H:%M", time.localtime()) + "\n" + phoneText)
        else:
            lcdInterface.setText_norefresh(str(check_output(['hostname', '-I'])))

    # If it is a new day, add a new day to phonedata
    if time.localtime().tm_mday != today:
        addDayToData()

    # Delay for server thread to do its tasks (delay might have to be lower myb .1 for button to work)
    time.sleep(0.1)
	
