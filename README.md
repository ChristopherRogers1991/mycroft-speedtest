# mycroft-speedtest
A Mycroft skill for running speedtests

## Short Demo
https://www.youtube.com/watch?v=1Tm56JKZcAg

## Setup

1. Clone this repo into your third party skills folder (the current default is ~/.mycroft/skills, but it used to be ~/.mycroft/third_party_skills; check your global/local mycroft.conf files if you have issues)
  * `cd ~/.mycroft/skills && git clone https://github.com/ChristopherRogers1991/mycroft-speedtest.git`
2. `cd` into the resulting `mycroft-speedtest` directory
  * `cd ~/.mycroft/skills/mycroft-speedtest`
3. If your mycroft instance runs in a virtual environment, activate it
  * `source ~/.virtualenvs/mycroft/bin/activate`
4. Install the required python libraries
  * `pip install -r requirements.txt`
5. Change skill options in the mycroft.home if desired (requires reboot)
  * https://www.speedtest.net/speedtest-servers.php

## Sample Phrases
1. Run a speedtest
2. What is my connection speed?