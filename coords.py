import time
import astropy.time
from astropy.time import Time, TimeJD
from datetime import datetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz


def convertTOaltaz(RA,DEC,lattitude,longitude):
    utc = datetime.now()

    Location = EarthLocation(lat=lattitude, lon=longitude, height = 100)
    Observer = AltAz(location= Location, obstime = utc)
    ST_COORDS = SkyCoord(RA,DEC, frame='icrs')
    ST_ALTAZ = ST_COORDS.transform_to(Observer)

    AZ = ST_ALTAZ.az.deg
    ALT = ST_ALTAZ.alt.deg

    return([str(ALT), str(AZ)])
