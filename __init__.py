from mycroft import MycroftSkill, intent_file_handler


class SunriseSunset(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('sunset.sunrise.intent')
    def handle_sunset_sunrise(self, message):
        self.speak_dialog('sunset.sunrise')


def create_skill():
    return SunriseSunset()

