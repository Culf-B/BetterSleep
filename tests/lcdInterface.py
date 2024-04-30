import json
import time
import sys
import os
PATH = os.path.dirname(os.path.abspath(__file__))
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#Set Button and LED pins
BUTTON_PIN = 23
#Setup Button and LED
GPIO.setup(BUTTON_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)

if sys.platform == 'uwp':
        import winrt_smbus as smbus
        bus = smbus.SMBus(1)
else:
        import smbus
        rev = GPIO.RPI_REVISION
        if rev == 2 or rev == 3:
                bus = smbus.SMBus(1)
        else:
                bus = smbus.SMBus(0)

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
        bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
        bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
        bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
        bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
        bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)
def textCommand(cmd):
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)
def setText(text):
        textCommand(0x01) # clear display
        time.sleep(.05)
        textCommand(0x08 | 0x04) # display on, no cursor
        textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        for c in text:
                if c == '\n' or count == 16:
                        count = 0
                        row += 1
                        if row == 2:
                                break
                        textCommand(0xc0)
                        if c == '\n':
                                continue
                count += 1
                bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

#Update the display without erasing the display
def setText_norefresh(text):
        textCommand(0x02) # return home
        time.sleep(.05)
        textCommand(0x08 | 0x04) # display on, no cursor
        textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        while len(text) < 32: #clears the rest of the screen
                text += ' '
        for c in text:
                if c == '\n' or count == 16:
                        count = 0
                        row += 1
                        if row == 2:
                                break
                        textCommand(0xc0)
                        if c == '\n':
                                continue
                count += 1
                bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

buttonPressed = False
buttonEvent = False
notification = False
notifications = []
updateTime = time.time()
backgroundUpdateTime = 0
colors = [[255,255,255],[255,0,0],[0,255,0],[0,0,255]]
colorIndex = 0
defaultColorIndex = 0
colorChanged = True

DATAFILE = os.path.join(PATH,"data.json")
WATERFILE =     os.path.join(PATH,"watering.json")

def getPlants():
        needsSaving = False
        # Load datafiles
        with open(DATAFILE, "r") as f:
                plants = json.load(f)
        with open(WATERFILE, "r") as f:
                try:
                        watertimes = json.load(f)
                except:
                        watertimes = {}
        # Remove items from watering.json if they are not in data.json
        done = False
        while not done:
                done = True
                for name in watertimes.keys():
                        exists = False
                        for plant in plants["plants"]:
                                if plant["name"] == name:
                                        exists = True
                                        break
                        if not exists:
                                watertimes.pop(name)
                                needsSaving = True
                                done = False
                                break
        # Add items to watering.json if they are in data.json
        for plant in plants["plants"]:
                if not plant["name"] in watertimes.keys():
                        watertimes[plant["name"]] = {"watered":time.time(),"watertime":float(plant["time"])*24*60*60}
                        needsSaving = True
        # Save if changes were made
        if needsSaving:
                with open(WATERFILE, "w") as f:
                        json.dump(watertimes, f)
        return plants, watertimes

def saveWatertimes(watertimes):
        # Save to file
        with open(WATERFILE, "w") as f:
                json.dump(watertimes, f)

def updateNotification():
        if notification:
                setText_norefresh(notifications[0])
                print(notifications[0])
        else:
                try:
                        setText_norefresh("Everything is good ( :")
                except IOError as e:
                        print(e)
                print("Everything is good ( :")
                colorIndex = 0
                colorChanged = True

plants, waterTimes = getPlants()
updateNotification()

while True:
        # Update plants every 5 seconds
        if updateTime + 5 <= time.time():
                updateTime = time.time()
                plants, waterTimes = getPlants()

                # Update watering
                for name, value in waterTimes.items():
                        if value["watered"] + value["watertime"] <= time.time(): # If plant needs watering
                                if not name in notifications: # If it is not already in notifications
                                        notifications.append(name)
                                        notification = True
                                        updateNotification()

        if colorChanged:
                setRGB(colors[colorIndex][0],colors[colorIndex][1],colors[colorIndex][2])
                print("Color changed to ", colors[colorIndex])
                colorChanged = False

        button_state = GPIO.input(BUTTON_PIN)
        if button_state == 0:
                buttonPressed = True
        else:
                if buttonPressed:
                        buttonEvent = True
                buttonPressed = False
        if buttonEvent:
                if notification:
                        name = notifications.pop(0)
                        if waterTimes[name]:
                                waterTimes[name]["watered"] = time.time()
                        saveWatertimes(waterTimes)
                        if len(notifications) == 0:
                                notification = False
                        updateNotification()
                        buttonEvent = False

        # Update background color
        # Update plants every 5 seconds
        if backgroundUpdateTime + 1 <= time.time():
                if notification:
                        if colorIndex < len(colors)-2:
                                colorIndex += 1
                        else:
                                colorIndex = 0
                        colorChanged = True
                else:
                        if colorIndex != 0:
                                colorIndex = 0
                                colorChanged = True
                backgroundUpdateTime = time.time()