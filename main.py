import functions_framework

from datetime import timedelta, datetime
import json

from skyfield.api import load

ts = load.timescale()
planets = load('de421.bsp')
earth = planets['earth']

planet_ephemeris = {
    'Mercury': planets['mercury'],
    'Venus': planets['venus'],
    'Mars': planets['mars'],
    'Jupiter': planets['jupiter barycenter'],  
    'Saturn': planets['saturn barycenter'],    
    'Uranus': planets['uranus barycenter'],    
    'Neptune': planets['neptune barycenter'],  
    'Moon': planets['moon']  
}

@functions_framework.http
def getEphemeris(request):
    request_args = request.args

    start = None
    if request_args and 'start' in request_args:
        start_arg = request_args['start']
        start = float(start_arg)


    length = None
    if request_args and 'length' in request_args:
        length_arg = request_args['length']
        length = float(length_arg)

    entries = []

    t_start = ts.tt_jd(start)
    t_end = t_start + length
    t_interval = 1/24

    t = t_start
    while t.tt < t_end.tt:
        for planet_name, planet in planet_ephemeris.items():
            position = earth.at(t).observe(planet)
            ra = position.apparent().radec(epoch='date')[0]
            dec = position.apparent().radec(epoch='date')[1]
            entries.append(EphemerisEntry(planet_name, t.tt, ra._degrees, dec.degrees))

        t+=t_interval
    
    return json.dumps([ob.__dict__ for ob in entries], cls=EphemerislObjectEncoder)


class EphemerisEntry():
    def __init__(self, name, time, ra, dec,):
        self.name = name
        self.time = time
        self.ra = ra
        self.dec = dec
    def reprJSON(self):
        return dict(name=self.name, 
                    time=self.time, 
                    ra=self.ra, 
                    dec=self.dec)
        
    
class EphemerislObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj) 
