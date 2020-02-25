from mycroft import MycroftSkill, intent_file_handler
from datetime import date, timedelta, datetime, time, tzinfo
import math

"""
Sunrise/Sunset Mycroft Skill

Source for the sunrise/sunset calculation python code is:
- Carlos Platoni - http://thorpesoftware.com/calculating-sunrise-and-sunset/

General sunrise/sunset related articles:
- Wikipedia - https://en.wikipedia.org/wiki/Sunrise_equation
- http://users.electromagnetic.net/bu/astro/sunrise-set.php
- http://aa.quae.nl/en/reken/zonpositie.html
"""

class SunriseSunset(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.date = date.today()
        self.longitude = None
        self.latitude = None

    def initialize(self):
        self.add_event('configuration.updated', self.handler_configuration_updated)
        self.load_configuration()
        self.register_entity_file('daytime.entity')
        self.register_entity_file('orb.entity')
        self.register_entity_file('action.entity')
        self.register_entity_file('event.entity')
        self.register_entity_file('date.entity')

    def stop(self):
        pass

    """ Reload coordinates if config has been updated """
    def handler_configuration_updated(self, message):
        self.load_configuration()
        return

    def load_configuration(self):
        self.longitude = float(self.settings.get('longitude'))
        self.latitude = float(self.settings.get('latitude'))
        return

    @intent_file_handler('set.rise.intent')
    def handle_set_rise(self, message):
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
            self.log.info("When is: " + str(when))
        else:
            when = ""

        """ Event can be sunrise, sunset, etc..."""
        if event is not None:
            self.log.info("Event is: " + str(event))

        if daytime is not None:
            self.speak("daytime is ")
            self.speak(str(daytime))

        """ Start calculation of rise/set events """
        sunrise_time,sunset_time = self.calc_sunrise_and_sunset(self.date)
        if event == "sunrise":
            in_future = self.is_time_in_future(sunrise_time)
            if in_future or when == "tomorrow":
                self.speak_dialog('sunriseFuture', data={"sunrise": str(sunrise_time), "when": when})
            else:
                self.speak_dialog('sunrisePast', data={"sunrise": str(sunrise_time), "when": when})
        elif event == "sunset":
            in_future = self.is_time_in_future(sunset_time)
            if in_future or when == "tomorrow":
                self.speak_dialog('sunsetFuture', data={"sunset": str(sunset_time), "when": when})
            else:
                self.speak_dialog('sunsetPast', data={"sunset": str(sunset_time), "when": when})
        else:
            self.speak("What?")
            #self.speak("Sunrise at ")
            #self.speak(str(sunrise_time))
            #self.speak("Sunset at ")
            #self.speak(str(sunset_time))


    def is_time_in_future(self, dt_event):
        dt_now = datetime.now().time()
        ms_now = self.time_to_miliseconds(dt_now)
        ms_event = self.time_to_miliseconds(dt_event)
        time_delta = ms_event - ms_now
        self.log.info("Time delta: " + str(time_delta))
        if int(time_delta.total_seconds()) < 0:
            return False
        return time_delta

    def calc_sunrise_and_sunset(self, dt):
        a=math.floor((14-dt.month)/12)
        y = dt.year+4800-a
        m = dt.month+12*a -3
        julian_date=dt.day+math.floor((153*m+2)/5)+365*y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)-32045

        nstar= (julian_date - 2451545.0 - 0.0009)-(self.longitude/360)
        n=round(nstar)
        jstar = 2451545.0+0.0009+(self.longitude/360) + n
        M=(357.5291+0.98560028*(jstar-2451545)) % 360
        c=(1.9148*self.sin_to_rad(M))+(0.0200*self.sin_to_rad(2*M))+(0.0003*self.sin_to_rad(3*M))
        l=(M+102.9372+c+180) % 360
        jtransit = jstar + (0.0053 * self.sin_to_rad(M)) - (0.0069 * self.sin_to_rad(2 * l))
        delta=math.asin(self.sin_to_rad(l) * self.sin_to_rad(23.45))*180/math.pi
        H = math.acos((self.sin_to_rad(-0.83)-self.sin_to_rad(self.latitude)*self.sin_to_rad(delta))/(self.cos_to_rad(self.latitude)*self.cos_to_rad(delta)))*180/math.pi
        jstarstar=2451545.0+0.0009+((H+self.longitude)/360)+n
        jset=jstarstar+(0.0053*self.sin_to_rad(M))-(0.0069*self.sin_to_rad(2*l))
        jrise=jtransit-(jset-jtransit)
        self.log.debug("Julian Sunrise: " + str(jrise))
        self.log.debug("Julian Sunset : " + str(jset))
        return (self.calculate_time_from_julian_date(jrise), self.calculate_time_from_julian_date(jset))

    def calc_moonrise_and_moonset(self, dt):
        pass

    def sin_to_rad(self, deg):
        return math.sin(deg * math.pi/180)

    def cos_to_rad(self, deg):
        return math.cos(deg * math.pi/180)

    def calculate_time_from_julian_date(self, jd):
        jd=jd+.5
        secs=int((jd-int(jd))*24*60*60+.5)
        mins=int(secs/60)
        hour=int(mins/60)
        return time(hour, mins % 60, secs % 60)

    """ Expects a datetime.time object and returns timedelta object """
    def time_to_miliseconds(self, tm):
        return timedelta(hours=tm.hour, minutes=tm.minute, seconds=tm.second, microseconds=tm.microsecond)

def create_skill():
    return SunriseSunset()
