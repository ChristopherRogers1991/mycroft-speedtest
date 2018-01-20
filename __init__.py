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
from mycroft.audio import wait_while_speaking

from pyspeedtest import SpeedTest
import time
from threading import Thread


__author__ = 'ChristopherRogers1991, Sujan4k0, Jarbas'


# speed test helpers

def intent_handler(function):
    """
    Decorator to add standard error handling to intent handlers.

    Parameters
    ----------
    function : callable

    Returns
    -------
    callable

    """
    def new_function(self, message):
        try:
            function(self, message)
        except Exception as e:
            logger.exception(e.message)
            self.speak_dialog('error')
    return new_function


def pretty_speed(speed):
    """
    Converts the speed to a more reasonable unit; modified from pyspeedtest's
    function which used 1024 instead of 1000 and spells out units instead

    Parameters
    ----------
    speed : float - speed in bytes per second

    Returns
    -------
    str

    """
    units = ['bits per second', 'kilobits per second', 'megabits per second',
             'gigabits per second']
    unit = 0
    while speed >= 1000:
        speed /= 1000
        unit += 1
    return '%0.2f %s' % (speed, units[unit])


def attempt_three_times(function):
    """
    Run function up to three times. If it fails after three attempts,
    raise the final exception it failed with.

    Parameters
    ----------
    function : callable

    Returns
    -------
    ? : The value returned by function

    Raises
    ------
    ? : The final exception function failed with after three attempts.

    """
    attempts = 0
    while attempts < 3:
        try:
            value = function()
            return value
        except Exception as e:
            attempts += 1
            if attempts == 3:
                raise
            msg = "Caught {error}: {message}. Retrying...".format(
                error=type(e), message=e.message)
            logger.warning(msg)


# Helpers for building the animation frames

def animate(t, often, func, *args):
    '''
    Args:
        t (int) : seconds from now to begin the frame (secs)
        often (int/string): (int) how often to repeat the frame (secs)
                            (str) when to trigger, relative to the clock,
                                  for synchronized repetitions
        func: the function to invoke
        *args: arguments to pass to func
    '''
    return {
        "time": time.time() + t,
        "often": often,
        "func": func,
        "args": args
    }


def _get_time(often, t):
    return often - t % often


class SpeedTestSkill(MycroftSkill):

    def __init__(self):
        super(SpeedTestSkill, self).__init__(name="SpeedTestSkill")
        self.speedtest = None
        if "host" not in self.settings:
            self.settings["host"] = None
        if "runs" not in self.settings:
            self.settings["runs"] = 2
        if "http_debug" not in self.settings:
            self.settings["http_debug"] = 0
        self.animations = []
        self.playing = False
        self.thread = None

    def run(self):
        """
        animation thread while performing speedtest

        """

        while self.playing:
            for animation in self.animations:
                if animation["time"] <= time.time():
                    # Execute animation action
                    animation["func"](*animation["args"])

                    # Adjust time for next loop
                    if type(animation["often"]) is int:
                        animation["time"] = time.time() + animation["often"]
                    else:
                        often = int(animation["often"])
                        t = animation["time"]
                        animation["time"] = time.time() + _get_time(
                            often, t)
            time.sleep(0.1)

        self.thread = None
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()
        self.enclosure.eyes_reset()

    def initialize(self):
        """
        Create and register intents

        """
        host = self.settings["host"]
        runs = int(self.settings["runs"])
        http_debug = int(self.settings["http_debug"])

        self.speedtest = SpeedTest(host=host, runs=runs, http_debug=http_debug)

        speedtest_intent = IntentBuilder("SpeedTestSkill")\
            .require("SpeedTestKeyword")\
            .build()

        self.register_intent(speedtest_intent, self.handle_speedtest_intent)

    @intent_handler
    def handle_speedtest_intent(self, message):
        """
        Run a speedtest, and speak the results.

        Parameters
        ----------
        message : Currently unused.

        """
        self.speak_dialog('start')
        wait_while_speaking()

        if not self.thread:
            self.playing = True

            # Display info on a screen
            self.enclosure.deactivate_mouth_events()
            self.enclosure.mouth_think()

            # Build the list of animation actions to run
            self.animations = [
                # look up down every 2 seconds, looping at 8 seconds
                animate(4, 8, self.enclosure.eyes_look, "d"),
                animate(6, 8, self.enclosure.eyes_look, "u"),

            ]

            self.thread = Thread(None, self.run)
            self.thread.daemon = True
            self.thread.start()

        ping = attempt_three_times(self.speedtest.ping)
        ping = str(round(ping, 1))

        download = attempt_three_times(self.speedtest.download)
        download = pretty_speed(download)

        upload = attempt_three_times(self.speedtest.upload)
        upload = pretty_speed(upload)

        self.playing = False
        self.speak("I have your results: Ping was " + ping + " milliseconds, "
                   + "the download speed was " + download +
                   ", and the upload speed was " + upload)

    def stop(self):
        if self.playing:
            self.playing = False  # the thread will kill itself
            return True
        else:
            return False


def create_skill():
    """
    Wraps the SpeedTestSkill constructor.

    Returns
    -------
    SpeedTestSkill

    """
    return SpeedTestSkill()
