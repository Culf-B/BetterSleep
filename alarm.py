class Alarm:
    def __init__(self, name, notifStyle = "Light", hour = None, minute = None):
        self.notifStyle = notifStyle
        self.name = name
        self.hour = hour
        self.minute = minute
        self.isOnCooldown = False # Alarm will not be able to ring for 1 minute after it has started
        if hour == None or minute == None:
            self.fullyDefined = False
        else:
            self.fullyDefined = True

    def checkRing(self, currentHour, currentMinute):
        if self.fullyDefined:
            if currentHour == self.hour and currentMinute == self.minute and self.isOnCooldown == False:
                self.isOnCooldown = True
                return True
            else:
                if self.isOnCooldown and currentMinute != self.minute:
                    self.isOnCooldown = False
                return False
        
    def setTime(self, hour = None, minute = None):
        self.hour = hour
        self.minute = minute
        if self.minute != minute:
            self.isOnCooldown = False

        if hour == None or minute == None:
            self.fullyDefined = False
        else:
            self.fullyDefined = True