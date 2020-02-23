from mycroft import MycroftSkill, intent_file_handler
from datetime import date, timedelta, datetime, time, tzinfo
import math

# Sources:
# Carlos Platoni - http://thorpesoftware.com/calculating-sunrise-and-sunset/
# Wikipedia - https://en.wikipedia.org/wiki/Sunrise_equation
# http://users.electromagnetic.net/bu/astro/sunrise-set.php
# http://aa.quae.nl/en/reken/zonpositie.html
def sin_to_rad(deg):
    return math.sin(deg * math.pi/180)

def cos_to_rad(deg):
    return math.cos(deg * math.pi/180)

def calculate_time_from_julian_date(jd):
    jd=jd+.5
    secs=int((jd-int(jd))*24*60*60+.5)
    mins=int(secs/60)
    hour=int(mins/60)
    return time(hour, mins % 60, secs % 60)

def calculate_date_from_julian_date(jd):
    dt = datetime.strptime(str(jd), '%y%j').strftime('%Y%m%d')
    return dt

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
        """ Only bother calculating stuff when we know at what location we are. """
        if self.longitude is None or self.latitude is None:
            self.speak("Sorry I don't know my exact position. Can you please configure your G.P.S. coordinates in the skill settings?")
            return

        orb = message.data.get('orb')
        when = message.data.get('date')
        event = message.data.get('event')
        daytime = message.data.get('daytime')

        if orb is not None:
            self.speak("orb is ")
            self.speak(str(orb))

        """ Change date if not today """
        if when is not None:
            if when == "tomorrow":
                self.date = datetime.now() + timedelta(days=1)
                self.speak("date tomorrow is " + str(self.date))

            self.log.info("When is: " + str(when)))

        if event is not None:
            self.log.info("Event is: " + str(event))

        if daytime is not None:
            self.speak("daytime is ")
            self.speak(str(daytime))

        """ Start calculation of rise/set events """
        sunrise,sunset = self.calc_sunrise_and_sunset(self.date)

        #self.speak_dialog('sunset.sunrise')
        if event == "sunrise":
            self.speak(str(self.time_has_passed(sunrise)))
            self.speak("The sun will rise at ")
            self.speak(str(sunrise))
        elif event == "sunset":
            self.speak(str(self.time_has_passed(sunset)))
            self.speak("The sun will set at ")
            self.speak(str(sunset))
        else:
            self.speak("Sunrise at ")
            self.speak(str(sunrise))
            self.speak("Sunset at ")
            self.speak(str(sunset))

    def time_has_passed(self, dt):
        dt_when = self.date
        dt_event = dt
        return dt_when - dt_event

    def calc_sunrise_and_sunset(self, dt):
        a=math.floor((14-dt.month)/12)
        y = dt.year+4800-a
        m = dt.month+12*a -3
        julian_date=dt.day+math.floor((153*m+2)/5)+365*y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)-32045

        nstar= (julian_date - 2451545.0 - 0.0009)-(self.longitude/360)
        n=round(nstar)
        jstar = 2451545.0+0.0009+(self.longitude/360) + n
        M=(357.5291+0.98560028*(jstar-2451545)) % 360
        c=(1.9148*sin_to_rad(M))+(0.0200*sin_to_rad(2*M))+(0.0003*sin_to_rad(3*M))
        l=(M+102.9372+c+180) % 360
        jtransit = jstar + (0.0053 * sin_to_rad(M)) - (0.0069 * sin_to_rad(2 * l))
        delta=math.asin(sin_to_rad(l) * sin_to_rad(23.45))*180/math.pi
        H = math.acos((sin_to_rad(-0.83)-sin_to_rad(self.latitude)*sin_to_rad(delta))/(cos_to_rad(self.latitude)*cos_to_rad(delta)))*180/math.pi
        jstarstar=2451545.0+0.0009+((H+self.longitude)/360)+n
        jset=jstarstar+(0.0053*sin_to_rad(M))-(0.0069*sin_to_rad(2*l))
        jrise=jtransit-(jset-jtransit)
        self.log.info("Julian Sunrise: " + str(jrise))
        self.log.info("Julian Sunset : " + str(jset))
        return (calculate_date_from_julian_date(jrise), calculate_date_from_julian_date(jset))
        # return (calculate_time_from_julian_date(jrise), calculate_time_from_julian_date(jset))


def create_skill():
    return SunriseSunset()
