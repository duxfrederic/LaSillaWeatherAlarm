from LaSillaWeatherAlerter import PhysicalMeasurement, WeatherReport,\
                                  CondensationRisk, TelescopesOpen, Alert
from config import property_lines



report = WeatherReport()

meas = {}
for key in property_lines.keys():
    if key == 'Domes Status':
        continue
    meas[key]= PhysicalMeasurement(key, report)
    print(key, meas[key].value, meas[key].status)
        
        
opens = TelescopesOpen(report)
print('Domes Status', opens.value, opens.status)


condensation = CondensationRisk(report)
print('Condensation Risk', condensation.value, condensation.status)


a = Alert(opens, 1, '>', howlong=2)
from time import sleep
print(opens.value)
print('no alarm')
print(a.check())
sleep(1)
print('no alarm')
print(a.check())

a.limit = 2
sleep(1.1)

print('no alarm')
print(a.check())

a.limit = 1

print('no alarm')
print(a.check())

sleep(1.1)

print('no alarm')
print(a.check())

sleep(1.)

print('alarm')
print(a.check())