import os
import argparse
import numpy as np
from itertools import repeat
import pandas as pd
try:
    from lsst.sims.movingObjects import Orbits
except ImportError:
    from orbits import Orbits
try:
    from lsst.sims.movingObjects import PyOrbEphemerides
except ImportError:
    from ooephemerides import PyOrbEphemerides


# Simple script to generate an ephemeris at a user-specified (TAI) time.

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Python script to generate ephemerides using oorb')
    parser.add_argument('--orbitFile', type=str, default=None, help='Input orbit file')
    parser.add_argument('--obsCode', type=str, default='I11', help='Observatory code for ephemerides')
    parser.add_argument('--ephTimesFile', type=str, default=None, help='Filename containing MJD (TAI) times for ephemerides')
    parser.add_argument('--ephTimes', type=str, default=None, help='List of MJD times for ephemerides (if >1: in quotes, separated by spaces')
    parser.set_defaults()
    args = parser.parse_args()


    # Read orbits.
    orbits = Orbits()
    orbits.readOrbits(args.orbitFile)
    print('Read %d orbits, first one with epoch of %f.' % (len(orbits), orbits.orbits.epoch.iloc[0]))

    # Set up ephemeris generation.
    pyephems = PyOrbEphemerides()

    print(pyephems.ephfile)
    # set observatory code
    obscode = args.obsCode

    # Set up dates to predict ephemerides.
    if args.ephTimes is not None:
        times = np.array(args.ephTimes.split(), float)
        obshistids = np.arange(0, len(times))

    elif args.ephTimesFile is not None:
        times = pd.read_table(args.ephTimesFile, delim_whitespace=True, names=['times'])
        times = times['times'].values

    else:
        raise Exception('Did not have any ephemeride times')

    #print "Using times: ", times

    # Generate ephemerides.
    pyephems.setOrbits(orbits)
    ephs = pyephems.generateEphemerides(times, obscode=obscode, timeScale='TAI', ephMode='N', byObject=True)

    print('ObjId MJD(TAI) RA Dec dRAdt dDecdt Geo_Dist Helio_Dist magV Elongation')
    for e, o in zip(ephs, orbits):
        for i in range(len(e)):
            print(o.orbits.objId.iloc[0], e['time'][i], e['ra'][i], e['dec'][i], e['dradt'][i], e['ddecdt'][i],
                  e['geo_dist'][i], e['helio_dist'][i], e['magV'][i], e['solarelon'][i])
