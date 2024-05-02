import RPi.GPIO as GPIO
import time
import json

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Datalogging array
data = []
endHour = 7
interval = 10
prevHour = time.localtime().tm_hour

# Function is commented in the ultrasonicTest.py file
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def saveData(n = "collection"):
    with open(str(n) + ".json", "w") as f:
        json.dump({"data": data}, f)

# Mainloop
print("Datacollection started")
while time.localtime().tm_hour != endHour:
    tempDist = round(distance(), 2)
    print(tempDist)
    data.append(tempDist)
    time.sleep(interval)

    # Data autosave
    if prevHour != time.localtime().tm_hour:
        prevHour = time.localtime().tm_hour
        saveData(prevHour)
        print("Data autosaved")

print("Datacollection ended")

saveData()
print("Data saved")