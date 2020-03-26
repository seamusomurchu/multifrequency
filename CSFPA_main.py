import qubic
import glob
import numpy as np
import os
import timeit
from CSFPA_dataIO import getXYcoords, dataIO, dataAnalysis, SaveVars, IntensityCalc, IntensityCalcRAW
from qubicpack.utilities import Qubic_DataDir
import qubic

def MainProg(filename, rep, pklrep, tesdatrep):
    
    start = timeit.default_timer()
    repfile=filename
#     repfile = rep + filename
#     basedir = '/home/james/eclipse-workspace/qubiclmou2/'
#     dictfilename = basedir + '/qubic/qubic/scripts/global_source.dict'
#     d = qubic.qubicdict.qubicDict()
#     d.read_from_file(dictfilename)
    # Use a tool from qubicpack to get a path
    basedir = Qubic_DataDir(datafile='instrument.py', ) 
    print('basedir : ', basedir)
    dictfilename = basedir + '/dicts/global_source_oneDet.dict'
    d = qubic.qubicdict.qubicDict()
    d.read_from_file('../qubic/qubic/dicts/global_source_oneDet.dict')    
    q = qubic.QubicMultibandInstrument(d)
    
    vtxs = q[0].detector.vertex
    vtxcounter = np.zeros(992)
    
    MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY = getXYcoords(repfile, vtxs)
    print('getxycoordfunctest', max(MagXarr), MagXarr.shape)
    
    vtxcounter = np.vstack((vtxcounter, vtxcntarr))
    vtxcounter = vtxcounter.T
    vtxcounter = vtxcounter[:, 1:3]
    
    IntX, IntY, IntT = IntensityCalc(MagXarr, PhaXarr, MagYarr, PhaYarr)
    print('intensity tests shape max', IntX.shape, max(IntX))
    
    dat = np.vstack((MagXarr,
     PhaXarr,
     ReXarr,
     ImXarr,
     MagYarr,
     PhaYarr,
     ReYarr,
     ImYarr,
     vtxcntarr,
     PixCenX,
     PixCenY,
     IntX,
     IntY,
     IntT))
    dat = dat.T
    dataIO(dat, tesdatrep, filename)
    datmodstring = 'datmod'
    datmod = dataAnalysis(dat)
    dataIO(datmod, tesdatrep, filename)
    dataCF1 = np.loadtxt(repfile, skiprows=1)
    
    xycoords = np.array(dataCF1[:, 2:4])
    freq = dataCF1[0, 10]
    print('frequency', freq)
    
    Ix, Iy, IT = IntensityCalcRAW(repfile)
    ITnans = [ (np.nan if x == 0 else x) for x in IT ]
    ITnans = np.asarray(ITnans)
    
    SaveVars(MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freq, pklrep)
    
    os.system('spd-say "Main program has finished"')
    stop = timeit.default_timer()
    time = stop - start
    seconds = (time - int(time)) * 60
    print(time / 60, 'm', seconds, 's')