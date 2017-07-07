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


__author__ = 'ChristopherRogers1991, Sujan4k0'
logger = getLogger(__name__)

bitrate_abbreviation_to_spelled_out_name = {
        "bps" : "bits per second",
        "Kbps": "kilobits per second",
        "Mbps": "megabits per second",
        "Gbps": "gigabits per second"
    }

def intent_handler(function):
    def new_function(self, message):
        try:
            function(self, message)
        except Exception as e:
            logger.exception(e.message)
            self.speak_dialog('error')
    return new_function

def pretty_speed(speed):
    units = ['bps', 'Kbps', 'Mbps', 'Gbps']
    unit = 0
    while speed >= 1000:
        speed /= 1000
        unit += 1
    return '%0.2f %s' % (speed, units[unit])

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
        self.enclosure.mouth_text(ping + " ms")

        download = pretty_speed(self.speedtest.download())
        self.enclosure.mouth_text(download)

        upload = pretty_speed(self.speedtest.upload())
        self.enclosure.mouth_text(upload)

        download = convert_bitrate_abbreviation_to_spelled_out_name(download)
        upload = convert_bitrate_abbreviation_to_spelled_out_name(upload)

        self.speak("Ping was " + ping + " milliseconds, " +
                   "the download speed was " + download +
                   " and the upload speed was " + upload)
        self.enclosure.reset()

    def stop(self):
        pass

def create_skill():
    return SpeedTestSkill()
