import numpy as np
import matplotlib.pyplot as plt

import lsst.sims.photUtils as photUtils
import lsst.sims.catUtils as catUtils
import lsst.sims.GalSimInterface as galsimInterface
from lsst.obs.lsstSim import LsstSimMapper

from lsst.sims.utils import ObservationMetaData
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator


opsdb = '/Users/lynnej/opsim/db/minion_1016_sqlite.db'
generator = ObservationMetaDataGenerator(database=opsdb, driver='sqlite')

obshistid = 222155
query = 'select fieldRA, fieldDec, expMJD, rotSkyPos, filter, FWHMeff, rawSeeing, fiveSigmaDepth, obsHistId '     'from summary where obshistid=%d' % obshistid
res = generator.opsimdb.execute_arbitrary(query)
fieldRA = np.degrees(float(res[0][0]))
fieldDec = np.degrees(float(res[0][1]))
expMJD = float(res[0][2])
rotSkyPos = np.degrees(float(res[0][3]))
bandpass = str(res[0][4])
fwhmeff = float(res[0][5])
rawseeing = float(res[0][6])
m5 = float(res[0][7])
print(obshistid, expMJD, fieldRA, fieldDec, bandpass, fwhmeff, m5)
stepsize = 20.0/60.0/24.0
times = np.arange(expMJD, expMJD + stepsize*7 + stepsize/2.0, stepsize)
#times = np.array([expMJD], float)
print('times {}'.format(times))


PSF = galsimInterface.Kolmogorov_and_Gaussian_PSF(rawSeeing=rawseeing)
photParams = photUtils.PhotometricParameters(exptime=30., nexp=1)
ssmObj = catUtils.baseCatalogModels.SolarSystemObj()
starObj = catUtils.baseCatalogModels.StarObj()
galaxyBulgeObj = catUtils.baseCatalogModels.GalaxyBulgeObj()
galaxyDiskObj = catUtils.baseCatalogModels.GalaxyDiskObj()
allowed_chips = ['R:2,2 S:0,0']

for i, expMJD in enumerate(times):
    obs = ObservationMetaData(pointingRA = fieldRA, pointingDec = fieldDec,
                             boundType='circle', boundLength=2.1,
                             mjd = expMJD, rotSkyPos = rotSkyPos,
                             bandpassName = bandpass, m5 = m5 + 0.75, seeing = fwhmeff)

    ssmcat = galsimInterface.GalSimSSM(ssmObj, obs_metadata=obs)
    ssmcat.camera = LsstSimMapper().camera
    ssmcat.photParams = photParams
    ssmcat.noise_and_background = galsimInterface.ExampleCCDNoise(addNoise=True, addBackground=True)
    ssmcat.allowed_chips = allowed_chips
    ssmcat.setPSF(PSF)
    ssmcat.write_catalog('just_ssm_%d_2.txt' % i)
    ssmcat.write_images(nameRoot='ssmimage_%d' % i)

# Constrain stars and galaxies to make this run a little faster
# Small boundLength because I'm simulating center CCD
for i, expMJD in enumerate(times):
    obs = ObservationMetaData(pointingRA = fieldRA, pointingDec = fieldDec,
                             boundType='circle', boundLength=0.5, #boundLength=2.1,
                             mjd = expMJD, rotSkyPos = rotSkyPos,
                             bandpassName = bandpass, m5 = m5 + 0.75, seeing = fwhmeff)

    ssmcat = galsimInterface.GalSimSSM(ssmObj, obs_metadata=obs)
    ssmcat.camera = LsstSimMapper().camera
    ssmcat.photParams = photParams
    ssmcat.noise_and_background = galsimInterface.ExampleCCDNoise(addNoise=True, addBackground=True)
    ssmcat.allowed_chips = allowed_chips
    ssmcat.setPSF(PSF)
    ssmcat.write_catalog('just_ssm_%d.txt' % i)
    starcat = galsimInterface.GalSimStars(starObj, obs_metadata=obs,
                                          constraint='rmag between 18.0 and 25.5')
    starcat.allowed_chips = allowed_chips
    starcat.copyGalSimInterpreter(ssmcat)
    starcat.write_catalog('just_stars_%d.txt' % i, chunk_size=10000)
    galbulgecat = galsimInterface.GalSimGalaxies(galaxyBulgeObj, obs_metadata=obs,
                                                 constraint='r_ab between 18.0 and 25.5')
    galbulgecat.allowed_chips = allowed_chips
    galbulgecat.copyGalSimInterpreter(starcat)
    galbulgecat.write_catalog('just_bulge_galaxies_%d.txt' % i, chunk_size=10000)
    galdiskcat = galsimInterface.GalSimGalaxies(galaxyDiskObj, obs_metadata=obs,
                                                constraint='r_ab between 18.0 and 25.5')
    galdiskcat.allowed_chips = allowed_chips
    galdiskcat.copyGalSimInterpreter(galbulgecat)
    galdiskcat.write_catalog('just_disk_galaxies_%d.txt' % i, chunk_size=10000)
    galdiskcat.write_images(nameRoot='image_%d' % i)



