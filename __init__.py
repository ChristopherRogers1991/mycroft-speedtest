"""
mycroft-speedtest : A Mycroft skill for running speedtests

Copyright (C) 2017  Christopher Rogers, Sujan Patel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from pyspeedtest import SpeedTest
from os.path import dirname
from collections import OrderedDict


__author__ = 'ChristopherRogers1991, Sujan4k0'
logger = getLogger(__name__)

# Ordered dictionary used to convert unit into 'speakable' text
bitrate_abbreviation_to_spelled_out_name = OrderedDict()
bitrate_abbreviation_to_spelled_out_name["Kbps"] = "kilobits per second"
bitrate_abbreviation_to_spelled_out_name["Mbps"] = "megabits per second"
bitrate_abbreviation_to_spelled_out_name["Gbps"] = "gigabits per second"
bitrate_abbreviation_to_spelled_out_name["bps"] = "bits per second"

def intent_handler(function):
    def new_function(self, message):
        try:
            function(self, message)
        except Exception as e:
            logger.exception(e.message)
            self.speak_dialog('error')
    return new_function

# Converts the speed to a more reasonable unit; modified from import's function which used 1024
# instead of 1000
def pretty_speed(speed):
    units = ['bps', 'Kbps', 'Mbps', 'Gbps']
    unit = 0
    while speed >= 1000:
        speed /= 1000
        unit += 1
    return '%0.2f %s' % (speed, units[unit])

# Converts a unit postfix into mycroft 'speakable' text
def convert_bitrate_abbreviation_to_spelled_out_name(speed_str):
    for abbrevation, spelled_out_name in bitrate_abbreviation_to_spelled_out_name.iteritems():
        speed_str = speed_str.replace(abbrevation, spelled_out_name)
    return speed_str

class SpeedTestSkill(MycroftSkill):

    def __init__(self):
        super(SpeedTestSkill, self).__init__(name="SpeedTestSkill")
        self.speedtest = None

    def initialize(self):
        self.load_data_files(dirname(__file__))
        host = self.config.get("host")
        runs = int(self.config.get("runs", 2))
        http_debug = int(self.config.get("http_debug", 0))

        self.speedtest = SpeedTest(host=host, runs=runs, http_debug=http_debug)

        speedtest_intent = IntentBuilder("SpeedTestSkill")\
            .require("SpeedTestKeyword") \
            .build()

        self.register_intent(speedtest_intent,
                             self.handle_speedtest_intent)

    @intent_handler
    def handle_speedtest_intent(self, message):

        ping = str(round(self.speedtest.ping(), 1))
        download = convert_bitrate_abbreviation_to_spelled_out_name(pretty_speed(self.speedtest.download()))
        upload = convert_bitrate_abbreviation_to_spelled_out_name(pretty_speed(self.speedtest.upload()))

        self.speak("Ping was " + ping + " milliseconds, " +
                   "the download speed was " + download +
                   " and the upload speed was " + upload)

    def stop(self):
        pass

def create_skill():
    return SpeedTestSkill()
