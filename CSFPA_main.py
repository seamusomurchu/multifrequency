import qubic
import glob
import numpy as np
import os
import timeit
from CSFPA_dataIO import getXYcoords, dataIO, dataAnalysis, SaveVars, IntensityCalc, IntensityCalcRAW, RetrieveVars
from qubicpack.utilities import Qubic_DataDir
import qubic

def MainProg(filepath, pklrep, tesdatrep):
    
    start = timeit.default_timer()
    repfile=filepath
    #strip Modal qb filename from filepath
    qbfilename = os.path.splitext(os.path.basename(repfile))[0]

    # Use a tool from qubicpack to get a path
    basedir = Qubic_DataDir(datafile='instrument.py', ) 
    print('basedir : ', basedir)
    dictfilename = basedir + '/dicts/global_source_oneDet.dict'
    d = qubic.qubicdict.qubicDict()
    #d.read_from_file('../qubic/qubic/dicts/global_source_oneDet.dict')
    #change to moddded dictionary
    d.read_from_file('../qubic/qubic/dicts/global_source_oneDetFI.dict')
    q = qubic.QubicMultibandInstrument(d)
    
    vtxs = q[0].detector.vertex
    vtxcounter = np.zeros(992)
    print("vertexes shape: ", vtxs.shape)
    
    MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY = getXYcoords(filepath, vtxs)
    print('getxycoordfunctest', max(MagXarr), MagXarr.shape)
    
    vtxcounter = np.vstack((vtxcounter, vtxcntarr))
    vtxcounter = vtxcounter.T
    vtxcounter = vtxcounter[:, 1:3]
    
    #caluclate and return instensity values for given mag & phase PIXELS
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
    
    #save the mag&pha data with the calculated intensity values PIXELS
    #chose whether to bother even saving the un-normed data if it just gets overwitten
    #dataIO(dat, tesdatrep, qbfilename)
    datmodstring = 'datmod'
    #dataAnalysis function normalises the data PIXELS
    datmod = dataAnalysis(dat)
    dataIO(datmod, tesdatrep, qbfilename)
    
    #load MODAL style data point data
    dataCF1 = np.loadtxt(repfile, skiprows=1)
    xycoords = np.array(dataCF1[:, 2:4])
    freq = dataCF1[0, 10]
    print('frequency', freq)
    
    #return intensity values for data points in the MODAL style
    Ix, Iy, IT = IntensityCalcRAW(repfile)
    ITnans = [ (np.nan if x == 0 else x) for x in IT ]
    ITnans = np.asarray(ITnans)
    
    #save in a folder as pickle files with all data accesible.
    SaveVars(MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, qbfilename, freq, pklrep)
    
    os.system('spd-say "Main program has finished"')
    stop = timeit.default_timer()
    time = stop - start
    seconds = (time - int(time)) * 60
    print(time / 60, 'm', seconds, 's')