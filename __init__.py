from mycroft import MycroftSkill, intent_file_handler
from datetime import date, timedelta, datetime, time, tzinfo
import math

# Sources:
# Carlos Platoni - http://thorpesoftware.com/calculating-sunrise-and-sunset/
# Wikipedia - https://en.wikipedia.org/wiki/Sunrise_equation
# http://users.electromagnetic.net/bu/astro/sunrise-set.php
# http://aa.quae.nl/en/reken/zonpositie.html
def sinrad(deg):
    return math.sin(deg * math.pi/180)

def cosrad(deg):
    return math.cos(deg * math.pi/180)

def calculatetimefromjuliandate(jd):
    jd=jd+.5
    secs=int((jd-int(jd))*24*60*60+.5)
    mins=int(secs/60)
    hour=int(mins/60)
    return time(hour, mins % 60, secs % 60)


class SunriseSunset(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.date = date.today()
        self.longitude = None
        self.latitude = None

    def initialize(self):
        self.longitude = float(self.settings.get('longitude'))
        self.latitude = float(self.settings.get('latitude'))

    def stop(self):
        pass

    @intent_file_handler('sunset.sunrise.intent')
    def handle_sunset_sunrise(self, message):
        orb = message.data.get('orb')
        when = message.data.get('date')
        event = message.data.get('event')
        daytime = message.data.get('daytime')

        if orb is not None:
            self.speak("orb is ")
            self.speak(str(orb))

        if when is not None:
            self.speak("when is ")
            self.speak(str(when))

        if event is not None:
            self.speak("event is ")
            self.speak(str(event))

        if daytime is not None:
            self.speak("daytime is ")
            self.speak(str(daytime))

        if self.longitude is None or self.latitude is None:
            self.speak("Sorry I don't know my exact position. Can you please configure your G.P.S. coordinates in the skill settings?")
            return
        else:
            sunrise,sunset = self.calcsunriseandsunset(self.date)
            #self.speak_dialog('sunset.sunrise')
            if event == "sunrise":
                self.speak("The sun will rise at ")
                self.speak(str(sunrise))
            elif event == "sunset":
                self.speak("The sun will set at ")
                self.speak(str(sunset))
            else:
                self.speak("Sunrise at ")
                self.speak(str(sunrise))
                self.speak("Sunset at ")
                self.speak(str(sunset))


    def calcsunriseandsunset(self, dt):
        a=math.floor((14-dt.month)/12)
        y = dt.year+4800-a
        m = dt.month+12*a -3
        julian_date=dt.day+math.floor((153*m+2)/5)+365*y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)-32045

        nstar= (julian_date - 2451545.0 - 0.0009)-(self.longitude/360)
        n=round(nstar)
        jstar = 2451545.0+0.0009+(self.longitude/360) + n
        M=(357.5291+0.98560028*(jstar-2451545)) % 360
        c=(1.9148*sinrad(M))+(0.0200*sinrad(2*M))+(0.0003*sinrad(3*M))
        l=(M+102.9372+c+180) % 360
        jtransit = jstar + (0.0053 * sinrad(M)) - (0.0069 * sinrad(2 * l))
        delta=math.asin(sinrad(l) * sinrad(23.45))*180/math.pi
        H = math.acos((sinrad(-0.83)-sinrad(self.latitude)*sinrad(delta))/(cosrad(self.latitude)*cosrad(delta)))*180/math.pi
        jstarstar=2451545.0+0.0009+((H+self.longitude)/360)+n
        jset=jstarstar+(0.0053*sinrad(M))-(0.0069*sinrad(2*l))
        jrise=jtransit-(jset-jtransit)
        return (calculatetimefromjuliandate(jrise), calculatetimefromjuliandate(jset))


def create_skill():
    return SunriseSunset()
