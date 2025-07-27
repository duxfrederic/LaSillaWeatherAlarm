#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 03:31:55 2022

@author: fred
"""
from time import time
import FreeSimpleGUI as sg

from LaSillaWeatherAlerter import PhysicalMeasurement, WeatherReport,\
                                  CondensationRisk, TelescopesOpen, Alert,\
                                  ops, ring
from config import property_lines

report = WeatherReport()


sg.theme('Reddit')

opsk = '    '.join([op for op in ops.keys()])
text = f'Use a comparison operators:\n{opsk} , \nthen choose the limit category and' +\
        ' how long (in seconds)\nthe condition must remain true before ringing the alarm.'
layout = [[sg.Text(text)]]
layout += [[sg.Text(key, size=(20,1)),
            sg.InputText('', key=key+'cmp', size=(3,1)),
            sg.Radio('red', key, key=key+'-1'),
            sg.Radio('orange', key, key=key+'0'),
            sg.Radio('yellow', key, key=key+'1'),
            sg.Radio('green', key, key=key+'2'),
            sg.InputText('300', key=key+'duration', size=(5,1))
            ] for i,key in enumerate(list(property_lines.keys())+['Condensation Risk'])]
layout += [[sg.Button('Set alarms', key='-setalarm-'),
            sg.Button('Reset alarms', key='-resetalarm-'),
            sg.Button('Exit')]]
layout += [[sg.Text('An alarm will sound when any one of the conditions is fullfilled.')]]
layout += [[sg.Text('0 alarms set.', key='Nalarm')]]
layout += [[sg.Multiline('', key='alarmstats', size=(72, 9))]]



try:
    window = sg.Window('Alarm', layout)
    alarms = []
    while True:  # Event Loop
        event, values = window.read(timeout=500)
        if event == '-setalarm-':
            for key, item in values.items():
                if not key.endswith('cmp'):
                    continue
                cmp = item.strip()
                if not cmp in ops.keys():
                    continue
                key = key.replace('cmp', '')
                for level in ['-1', '0', '1', '2']:
                    if values[key+level]:
                        setlevel = level
                        break
                else:
                    continue
                if key == 'Domes Status':
                    meas = TelescopesOpen(report)
                elif key == 'Condensation Risk':
                    meas = CondensationRisk(report)
                else:
                    meas = PhysicalMeasurement(key, report)
                howlong = float(values[key+'duration'])
                alarms.append(Alert(meas, int(setlevel), cmp, howlong=howlong))

        if event == '-resetalarm-':
            alarms = []
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        window['Nalarm'].update(f"{len(alarms)} alarms set.")
        # at every loop:
        infotext = []
        for alarm in alarms:
            ms = alarm.measurement
            text = f"{ms.name}: value {ms.value} <-> {ms.status.name}," + \
                            f" alarm if {alarm.comp} {alarm.limitstatus.name}"
            if alarm.time_when_passed >0 :
                text += f" (time {time() - alarm.time_when_passed:.0f}/{alarm.howlong:.0f})"
            infotext.append(text)
        window['alarmstats'].update('\n'.join(infotext))
        window.refresh()

        for j, alarm in enumerate(alarms):
            if alarm.check():
                text = f"Wow an alarm! {alarm.measurement.name} is at {alarm.measurement.value}"
                out = ''
                while not out == 'OK':
                    ring()
                    out = sg.popup_auto_close(text, auto_close_duration=30)
                    print(out)
                del alarms[j]


except Exception as e:
    print(e)
finally:
    window.close()
