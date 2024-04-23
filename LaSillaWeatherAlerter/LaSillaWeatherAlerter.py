# -*- coding: utf-8 -*-
import os
import time
import playsound
from urllib.request import urlopen
from enum import Enum
import re
# for some, urllib complains about not being able to verify ssl.
# let us overwrite this as we do not need https.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import operator
ops = {
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt
}


from config import URL, property_lines, update_frequency

# propertylines: very unlikely to change, probably has been the same in
# the ESO weather HTML for 20 years
sound = os.path.join(os.path.dirname(__file__), 'assets', 'alarm.mp3')

class Status(Enum):
    RED = -1
    ORANGE = 0
    YELLOW = 1
    GREEN = 2


class WeatherReport:
    def __init__(self, url=URL, update_frequency=update_frequency):
        self.url = url
        self.update_frequency = update_frequency
        self.update()

    def getHTMLLines(self, url):
        content = urlopen(url)
        content = str(content.read()).split(r'\n')
        return content

    def update(self):
        self._html_lines = self.getHTMLLines(self.url)
        self.last_update = time.time()

    @property
    def html_lines(self):
        if time.time() - self.last_update > self.update_frequency:
            self.update()
        return self._html_lines


class Measurement:
    def __init__(self, name : str, report : WeatherReport):
        self.name = name
        self.report = report

    @property
    def status(self):
        self.parse()
        return self._status

    @property
    def value(self):
        self.parse()
        return self._value



class PhysicalMeasurement(Measurement):
    def parse(self):
        html_lines = self.report.html_lines
        line = property_lines[self.name]

        assert self.name in html_lines[line]
        r = re.compile(r"[-]?[0-9]+[.][0-9]*")
        value = r.findall(html_lines[line+1])
        assert len(value)==1
        value = float(value[0])
        lines = [line+2, line+3]
        for line in lines:
            if 'redball' in html_lines[line]:
                status = Status(-1)
                break
            elif 'orangeball' in html_lines[line]:
                status = Status(0)
                break
            elif 'yellowball' in html_lines[line]:
                status = Status(1)
                break
            elif 'greenball' in html_lines[line]:
                status = Status(2)
                break
        else:
            raise AssertionError("Unknown status or wrong line!\n"
                                 f"line {line}"
                                 f"{html_lines[line+2]}")
        self._value = value
        self._status = status


class TelescopesOpen(Measurement):
    def __init__(self, report):
        super().__init__(name='Domes Status', report=report)
    def parse(self):
        html_lines = self.report.html_lines
        line = property_lines[self.name]

        N_open = html_lines[line].count('green') - 1
        self._value = N_open
        # if all 3 are open, we probably good:
        if N_open == 3:
            self._status = Status(2)
        # if at least one is open, can't be dramatic:
        elif N_open >= 1:
            self._status = Status(1)
        # if all closed, probably not good:
        else:
            self._status = Status(-1)


class CondensationRisk(Measurement):
    def __init__(self, report : WeatherReport):
        super().__init__(name='Condensation Risk', report=report)
        self.temp = PhysicalMeasurement('Temperature', self.report)
        self.dew = PhysicalMeasurement('Dew Point', self.report)
    def parse(self):
        delta = self.temp.value - self.dew.value
        self._value = delta
        if delta >= 6:
            self._status = Status(2)
        elif delta >= 5:
            self._status = Status(1)
        elif delta >= 3:
            self._status = Status(0)
        else:
            self._status = Status(-1)



class Alert():
    def __init__(self, measurement, limit, comparison, howlong=0):
        self.measurement = measurement
        self.limit = limit
        self.limitstatus = Status(limit)
        self.comp = comparison
        # how much time one must be beyond the limit before alerting,
        # in seconds.
        self.howlong = howlong
        self.time_when_passed = 0

    def check(self):
        op = ops[self.comp]
        if op(self.measurement.status.value, self.limit):
            # immediately ring if waiting not desired:
            if self.howlong == 0:
                return 1
            # waiting desired, but first excursion in the alarm zone:
            if self.time_when_passed == 0:
                self.time_when_passed = time.time()
                return 0
            # if past the limit for a large enough amount of time:
            if self.time_when_passed + self.howlong < time.time() - 0.1:
                return 1
            return 0
        else:
            # if within allowed range, reset:
            self.time_when_passed = 0
            return 0

def ring():
    playsound.playsound(sound, block=False)

