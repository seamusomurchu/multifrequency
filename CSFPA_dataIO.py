import numpy as np
import pickle
import math
import pandas as pd
from scipy.interpolate import griddata
#doesn'treally make sense to have abberated cuts but okay
import matplotlib.pyplot as plt
from scipy.signal import chirp, find_peaks, peak_widths
import scipy

def getXYcoords(f, vtxs):

    print(f)
    data = np.loadtxt(f, skiprows=1)
    
    xycoords = np.array(data[:,2:4])
    
    cnti = 0
    cntj = 0
    
    MagXlist = np.array([])
    MagXarr = np.array([])
    
    PhaXlist = np.array([])
    PhaXarr = np.array([])
    
    MagYlist = np.array([])
    MagYarr = np.array([])
    
    PhaYlist = np.array([])
    PhaYarr = np.array([])
    
    ReXlist = np.array([])
    ReXarr = np.array([])
    
    ImXlist = np.array([])
    ImXarr = np.array([])
    
    ReYlist = np.array([])
    ReYarr = np.array([])
    
    ImYlist = np.array([])
    ImYarr = np.array([])
    #pixel centers
    PixCenX = np.array([])
    PixCenY = np.array([])
    
    vtxcntarr = ([])
    #count number of data points per pixel for analysis/normalisation
    vtxcnt = 0   
    
    for i in vtxs:
        cnti = cnti + 1
        cntj = 0
        #pixcenx = (i[0,0] + i[2,0]) / 2  #have to use vtxs here
        #print "pixcenx = ", pixcenx, type(pixcenx), type(PixCenX)
        #PixCenX.append(pixcenx)
        #pixceny = (i[0,1] + i[2,1]) / 2
        #PixCenY.append(pixceny)
        
        for j in xycoords:
            
            #x y are modal data points
            #x1,y1,x2,y2 are detector geometry points
            if f.endswith((".qb")):
                x = j[1]
                y = j[0]
            else:                
                x = j[0]
                y = j[1]
            x1 = i[0,0]
            y1 = i[0,1]
            x2 = i[2,0]
            y2 = i[2,1]
    
            #test if x and x1 are same unit
            #print "xandys", x, y, x1, y1

            if x >= x2 and x <= x1 and y >= y2 and y <= y1:
                #find mags and phases in pixel area
                MagXlist = np.append(MagXlist, data[cntj,4])
                PhaXlist = np.append(PhaXlist, data[cntj,5])
                MagYlist = np.append(MagYlist, data[cntj,6])
                PhaYlist = np.append(PhaYlist, data[cntj,7])
                #convert mags&phases to intensity
                ReX = data[cntj,4]*math.cos(data[cntj,5])
                #print "ReX test ",ReX,data[cntj,4],data[cntj,5]
                ReXlist = np.append(ReXlist,ReX)
                
                ImX = data[cntj,4]*math.sin(data[cntj,5])
                ImXlist = np.append(ImXlist,ImX)
                
                #Re Im in Y direction here
                ReY = data[cntj,6]*math.cos(data[cntj,7])
                ReYlist = np.append(ReYlist,ReY)
                ImY = data[cntj,6]*math.sin(data[cntj,7])
                ImYlist = np.append(ImYlist,ImY)
                
                #print "point exists in vertexes", x,y,x1,y1,x2,y2
                vtxcnt = vtxcnt + 1
                
            cntj = cntj + 1 
        
        #Do for Magnitude X
        MagXsum = sum(MagXlist)/len(MagXlist)
        MagXarr = np.append(MagXarr,MagXsum)    #Now set int and arr to zero for next loop
        MagXsum = 0
        MagXlist = np.array([])
        #Do for Phase X
        PhaXsum = sum(PhaXlist)/len(PhaXlist)
        PhaXarr = np.append(PhaXarr,PhaXsum)
        PhaXsum = 0
        PhaXlist = np.array([])
        #Do for Mag Y
        MagYsum = sum(MagYlist)/len(MagYlist)
        MagYarr = np.append(MagYarr,MagYsum)    #Now set int and arr to zero for next loop
        MagYsum = 0
        MagYlist = np.array([])       
        #Do for Phase Y
        PhaYsum = sum(PhaYlist)/len(PhaYlist)
        PhaYarr = np.append(PhaYarr,PhaYsum)
        PhaYsum = 0
        PhaYlist = np.array([])
        #Re, Im data
        ReXsum = sum(ReXlist)/len(ReXlist)
        ReXarr = np.append(ReXarr,ReXsum)
        ReXsum = 0
        ReXlist = np.array([])
        #ImX arr work
        ImXsum = sum(ImXlist)/len(ImXlist)
        ImXarr = np.append(ImXarr,ImXsum)
        ImXsum = 0
        ImXlist = np.array([])
        #Re Y data
        ReYsum = sum(ReYlist)/len(ReYlist)
        ReYarr = np.append(ReYarr,ReYsum)
        ReYsum = 0
        ReYlist = np.array([])
        #ImY arr work
        ImYsum = sum(ImYlist)/len(ImYlist)
        ImYarr = np.append(ImYarr,ImYsum)
        ImYsum = 0
        ImYlist = np.array([])
        #data points per pixel counter
        vtxcntarr = np.append(vtxcntarr,vtxcnt)
        vtxcnt = 0 
        #Pixel centers as array
        pixcenx = (x1 + x2) / 2        
        pixceny = (y1 + y2) / 2
        PixCenX = np.append(PixCenX,pixcenx)
        PixCenY = np.append(PixCenY,pixceny)
        #progperc = (float(cnti)/len(vtxs) ) *100
        #print "vertex loop percent estimate = ", progperc, "%"#, "file = ",f 
        
    #print "ReXarr test, =", ReXarr
    return MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY

def dataIO(dat, tesdatrep, string):
    
    f = open(tesdatrep + string + '.qbdat','w+')
    f.write('Summed detector Values' + '\n')
    f.write('MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT' + '\n')
    f.write('****DATA START***' + '\n')
    np.savetxt(f,dat,delimiter='    ',fmt='%17.9e')
    
    return 

def dataAnalysis(dat): 
    """MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT
       0        1        2       3       4        5        6       7       8          9        10       11    12    13  
    """
    #Cop DAT array and normalise data in datamod
    datmod = dat
	
	#ignore DIV zero errors
    np.seterr(divide='ignore', invalid='ignore')

    #account for "sampling/aliasing"
    datmod[:,0] = datmod[:,0]/datmod[:,8]
    #normalise to one/1
    datmod[:,0] = datmod[:,0]/max(dat[:,0])
    #Normalise PhaseX for pixels and unity
    datmod[:,1] = datmod[:,1]/datmod[:,8]
    datmod[:,1] = datmod[:,1]/max(dat[:,1])
    #norm ReX for pixels and unity
    datmod[:,2] = datmod[:,2]/datmod[:,8]
    datmod[:,2] = datmod[:,2]/max(dat[:,2])
    #norm ImX for pixels and unity
    datmod[:,3] = datmod[:,3]/datmod[:,8]
    datmod[:,3] = datmod[:,3]/max(dat[:,3])
    #norm MagY for pixels and unity
    datmod[:,4] = datmod[:,4]/datmod[:,8]
    datmod[:,4] = datmod[:,4]/max(dat[:,4])
    #norm PhaY for pixels and unity
    datmod[:,5] = datmod[:,5]/datmod[:,8]
    datmod[:,5] = datmod[:,5]/max(dat[:,5])
    #norm ReY for pixels and unity
    datmod[:,6] = datmod[:,6]/datmod[:,8]
    datmod[:,6] = datmod[:,6]/max(dat[:,6])
    #norm ImY for pixels and unity
    datmod[:,7] = datmod[:,7]/datmod[:,8]
    datmod[:,7] = datmod[:,7]/max(dat[:,7])
    #norm IntX for pixels and unity
    datmod[:,11] = datmod[:,11]/datmod[:,8]
    datmod[:,11] = datmod[:,11]/max(dat[:,11])
    #norm IntY for pixels and unity
    datmod[:,12] = datmod[:,12]/datmod[:,8]
    datmod[:,12] = datmod[:,12]/max(dat[:,12])
    #norm IntY for pixels and unity
    datmod[:,13] = datmod[:,13]/datmod[:,8]
    datmod[:,13] = datmod[:,13]/max(dat[:,13])
   
    return datmod

def SaveVars(MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freq, rep):
    # Saving the objects:
    #    with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    #        pickle.dump([MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT], f)
    #    return
    #orep = '/home/james/files4CSFPA/qbdataioOUTFILES/'
    f=open(rep + 'FPA_objs_' + filename + '.pkl', 'wb')
    pickle.dump(MagXarr,f)
    pickle.dump(PhaXarr,f)
    pickle.dump(ReXarr,f)
    pickle.dump(ImXarr,f)
    pickle.dump(MagYarr,f)
    pickle.dump(PhaYarr,f)
    pickle.dump(ReYarr,f)
    pickle.dump(ImYarr,f)
    pickle.dump(vtxcntarr,f)
    pickle.dump(PixCenX,f)
    pickle.dump(PixCenY,f)
    pickle.dump(IntX,f)
    pickle.dump(IntY,f)
    pickle.dump(IntT,f)
    pickle.dump(Ix,f)
    pickle.dump(Iy,f)
    pickle.dump(IT,f)
    pickle.dump(xycoords,f)
    pickle.dump(filename,f)
    pickle.dump(freq,f)
    
    return
    
def RetrieveVars(plotfname): 
    # Getting back the objects:
    #    with open('objs.pkl') as f:  # Python 3: open(..., 'rb')
    #        MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT = pickle.load(f)
    #    return MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT
    print("retrieving vars from ", plotfname)
    f=open(plotfname,'rb')
    MagXarr=pickle.load(f)
    PhaXarr=pickle.load(f)
    ReXarr=pickle.load(f)
    ImXarr=pickle.load(f)
    MagYarr=pickle.load(f)
    PhaYarr=pickle.load(f)
    ReYarr=pickle.load(f)
    ImYarr=pickle.load(f)
    vtxcntarr=pickle.load(f)
    PixCenX=pickle.load(f)
    PixCenY=pickle.load(f)
    IntX=pickle.load(f)
    IntY=pickle.load(f)
    IntT=pickle.load(f)
    Ix=pickle.load(f)
    Iy=pickle.load(f)
    IT=pickle.load(f)
    xycoords=pickle.load(f)
    filename=pickle.load(f)
    freq=pickle.load(f)
    
    return MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freq


def PixDataIO():   
    #retrieve variables saved as pickle package
    #save them as CSV style for analysis with raw TES data   
    MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename = RetrieveVars()
    
    #Format 'dat' in np.savetext from retrievevars
    #pixarr = np.vstack((PixCenX, PixCenY, IntT))
    
    TESnum = np.linspace(1,992,992,dtype=int)
    
    f = open('/home/james/CSFPA/PixDataIO' + '.qbdat','w+')
    f.write('Summed CF detector Values' + '\n')
    f.write('TESnum, Xpos, Ypos, Value' + '\n')
    f.write('****DATA START***' + '\n')
    #np.savetxt(f, (pixarr), delimiter='    ', fmt='%.5e')   
    for i in xrange(992):
        
        tesnum = str("%003i" % TESnum[i])
        xpos = str("%.5f" % PixCenX[i])
        ypos = str("%.5f" % PixCenY[i])
        value = str("%.5f" % IntT[i])      
        f.write(tesnum + '    ' + xpos + '    ' + ypos + '    ' + value + '\n')       
    f.close()
    
    return

def IntensityCalc(MagXarr, PhaXarr, MagYarr, PhaYarr):
	#so here i have to decide if i want to do this in magpha or reim
	#there is a nice ocw.mit acoustics reference from 2004 for this
	#do the calculatoin
	#return intensity X or Y
	#calculate total intensity back in main
	
	IntX = (MagXarr*np.cos(PhaXarr))**2 + (MagXarr*np.sin(PhaXarr))**2
	IntY = (MagYarr*np.cos(PhaYarr))**2 + (MagYarr*np.sin(PhaYarr))**2
	IntT = IntX[:] + IntY[:]
	
	return IntX, IntY, IntT
   
def IntensityCalcRAW(filename):
	#Do intensity calculation raw on file data .qb or .dat
    data = np.loadtxt(filename, skiprows=1)
	
    Ix = (data[:,4]*np.cos(data[:,5]))**2 + (data[:,4]*np.sin(data[:,5]))**2
    Iy = (data[:,6]*np.cos(data[:,7]))**2 + (data[:,6]*np.sin(data[:,7]))**2
    IT = Ix[:] + Iy[:]
    print("Intensity calculation shape test", IT.shape, max(IT))
	
    return Ix, Iy, IT

def kwavenum(freq):
	print("function takes frequency in GHz and returns wavenumber in per mm and lambda in mm")
	
	freq = float(freq) * 10**9
	
	lamb = (299792458 / freq) * 1000 #convert to mm and per mm with *1000
	
	wavenum = 2*np.pi / lamb
	
	return wavenum, freq, lamb

def FindGridArea(pklrep):
	#load pickle
	#pklrep = '/home/james/files4CSFPA/qbdataioOUTFILES/' + pkl
	MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freq = RetrieveVars(pklrep)
	#with filename from pickle load data
# 	qbrep = '/home/james/multifreqfiles/cf2outfiles/'
# 	qbrepfile = qbrep + filename
# 	print("***test file reps", qbrepfile, pklrep)
# 	data = np.loadtxt(qbrepfile, skiprows=1)
	gridmax = max(xycoords[:,0]) * 1000 #convert min and max from m to mm
	gridmin = min(xycoords[:,0]) * 1000
	gridarea = (gridmax - gridmin) **2
	
	return gridarea

def GridPowerCalc(pklrep):
	#pklrep = '/home/james/files4CSFPA/qbdataioOUTFILES/' + pkl
	#calculate total power on a GRASP focal plane
	fourpi = 4*np.pi
	freqGHz = 150 # assume this is standard for grasp models
	#load variables for a given FPA pickle file
	MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freqGHz = RetrieveVars(pklrep)
	#retrieve wavenumber info to calculate power with ksquared
	k, f, l = kwavenum(freqGHz)
	
	print("wavenum l in W/mm^2, freq in Hz, lambda in mm; ", k,f,l)

	#calculate power flux for area of a data point
	#use area box of each data point
	gridarea = FindGridArea(pklrep) #find area of grasp grid (in mm)
	pixarea = gridarea / len(xycoords) #find area of 'pixel' on grasp grid
	print("FP pix area", pixarea)
	print("grid area", gridarea)
	#calculate power of each data point on grid
	#IT[IT < 0.000059] = 0 #corresponds to GRASPS -85dB level
	P = IT * k**2 
	Pmean = np.mean(P) * gridarea
	PF = P * pixarea #calculate power flux area of each datapoint
	PFsum = np.sum(PF)
	#calculate power on grid with two methods
	pd = ((PFsum - fourpi) / fourpi) * 100 #%diff to 4pi
	#print results in line
	print("from mean power flux, sumed points, %diff", Pmean, PFsum, pd)
	#return array with power flux for each data point in grid
	return PF/fourpi

def TESPowerCalc(pklrep):
	#give pkl location
	#pklrep = '/home/james/files4CSFPA/qbdataioOUTFILES/' + pkl
	#calculate total power on a GRASP TES focal plane
	TESarea = 2.6 * 2.6 #mm^2
	fourpi = 4*np.pi
	#freqGHz = 150 # assume this is standard for grasp models
	#load variables for a given FPA pickle file
	MagXarr, PhaXarr, ReXarr, ImXarr, MagYarr, PhaYarr, ReYarr, ImYarr, vtxcntarr, PixCenX, PixCenY, IntX, IntY, IntT, Ix, Iy, IT, xycoords, filename, freqGHz = RetrieveVars(pklrep)
	#retrieve wavenumber info to calculate power with ksquared
	k, f, l = kwavenum(freqGHz)

	print("wavenum l in W/mm^2, freq in Hz, lambda in mm; ", k,f,l)

	#calculate power of each TES on focal plane
	TESPower = IntT * k**2 * TESarea / fourpi
	
	return TESPower

def OutputTESPower(TESPower,filename):
	#outfile location
	outF = open("/home/james/files4CSFPA/qbdataioOUTFILES/TESPowOfile"+filename+".txt", "w")
	#set up det nums from array
	pix = np.linspace(1,len(TESPower),len(TESPower), dtype=int)
	
	data = np.array([pix, TESPower]).T
	outF.write('Pixel Number as defined by qubicsoft vertexes | Power in Watts' + '\n')	        	  

	np.savetxt(outF, data, fmt='%i %1.4e', delimiter ='    ')
	#iterate through TES Power values
	#i = 0
	#for line in TESPower:
	  # write line to output file
	  #output header
		#outF.write('Pixel Number as defined by qubicsoft vertexes | Power in Watts')	        	  
		##outF.write(pix[i], '{:.4e}'.format(line))
		#outF.write("\n")
		#i+=1
	#outF.close()
	
	return

def GetMODALGridPixArea(fname):
	df = pd.read_csv(fname, sep='\t', header=0)
	maxX = max(df.X)
	minX = min(df.X)
	maxY = max(df.Y)
	minY = min(df.Y)
	
	lenX = (maxX - minX) / 1000 #length of one grid dimension in meters
	lenY = (maxY - minY) / 1000
	gridarea = lenX * lenY #grid area in meters^2
	pixarea = gridarea / len(df.X) #area of each data point
	
	return gridarea, pixarea
    
def ApFieldMag2ReIm(fpath, output):
    """not fully tested as of 21/09/21
    this should convert an aperture field file from mag phase to re im and
    save in grasp format
    give the input and output file paths you want"""

    #load and format data
    data = np.loadtxt(fpath, skiprows=1)
    df = pd.DataFrame(data, columns=['xind', 'yindx', 'xpos', 'ypos', 'xmag', 'xpha', 'ymag', 'ypha', 'poynz'])
    #calcualte real and imaginary
    rex = df.xmag * np.cos(df.xpha)
    imx = df.xmag * np.sin(df.xpha)
    rey = df.ymag * np.cos(df.ypha)
    imy = df.ymag * np.sin(df.ypha)
    #format data to save
    savedat = np.array([rex, imx])
    redu2 = np.append(savedat, np.zeros([4, len(rex)]), axis=0)
    #save the file with header
    header = 'Aperture field converted output from SCATTER/MODAL mag phase to GRASP format Re Im'+'\n'+'This is an ignorantly hardcoded header. See grasp manuals for you own header'+'\n'+'++++' + '\n'+'   1' + '\n'+'   1   3   3   3' + '\n'+'   0   0' + '\n'+'-6.167E-00 -6.167E-00 6.167E-00 6.167E-00' + '\n'+'101 101 0'
    np.savetxt(output, redu2.T, delimiter=' ',fmt='%5.6f', header=header, comments='')
    
    return

def IntegrateHornCombOnFP(it, xycoords, vtxs):
    """Pass in focal plane data combined in mag and phase. e.g. intensity array of 58081
    to integrate over bolometer area of 992 bolometers
    xycoords is a 2,58081 array of x y points
    pass in qubic vtxs array"""
    #xycoords = np.array(data[:,2:4])
    #bolometer arrays
    intbol = np.array([])
    bols= np.array([])
    #pixel centers
    PixCenX = np.array([])
    PixCenY = np.array([])
    
    cnti = 0
    cntj = 0
    vtxcntarr = ([])
    #count number of data points per pixel for analysis/normalisation
    vtxcnt = 0  
    for i in vtxs:
        cnti = cnti + 1
        cntj = 0
        
        for j in range(len(xycoords[0,:])):
            #if f.endswith((".qb")):
            #careful here about weird Y first thing from MODAL...
            x = xycoords[0, j]
            y = xycoords[1, j]
            #else:                
                #x = j[0]
                #y = j[1]
            x1 = i[0,0]
            y1 = i[0,1]
            x2 = i[2,0]
            y2 = i[2,1]
            
            if x >= x2 and x <= x1 and y >= y2 and y <= y1:
                #print(x,y, x1, y1, x2, y2)
                #if the point is inside the bolometer area, add to array
                intbol = np.append(intbol, it[cntj])
                
                vtxcnt = vtxcnt + 1
                
            cntj = cntj + 1
            
        #sum the values in bolometer area and append to the bolometer array
        bols = np.append(bols, sum(intbol))
        intbol = np.array([])
        
        #data points per pixel counter
        vtxcntarr = np.append(vtxcntarr,vtxcnt)
        vtxcnt = 0 
        #Pixel centers as array
        pixcenx = (x1 + x2) / 2        
        pixceny = (y1 + y2) / 2
        PixCenX = np.append(PixCenX,pixcenx)
        PixCenY = np.append(PixCenY,pixceny)
        
    return PixCenX, PixCenY, bols

def makemeshgrid(psfdata, meshsize):
    """ make a meshgrid out of .qb data (MODAL style/.dat files)
    useful for taking cuts of focal plane data"""
    x = np.linspace(min(psfdata[0,:]), max(psfdata[0,:]), meshsize)
    y = np.linspace(min(psfdata[1,:]), max(psfdata[1,:]), meshsize)

    X,Y = np.meshgrid(x, y)

    # Interpolate (x,y,z) points [mat] over a normal (x,y) grid [X,Y]
    #   Depending on your "error", you may be able to use other methods
    Z = griddata((psfdata[0,:], psfdata[1,:]), psfdata[2,:], (X,Y), method='nearest')
    
    return Z

def AbberatedCut(xdat, ydat, itdat, x0, y0, x1, y1, x2, y2, meshsize, prom, rel_height, norm=True, rpeaks=False):
    """it x and y dat should be same shape, points for cuts, meshsize"""

    mesh = np.zeros([1, meshsize, meshsize])
    mesh = makemeshgrid(np.array([xdat, ydat, itdat]), meshsize)

    azmin = min(xdat)
    azmax = max(xdat)
    elmin = min(ydat)
    elmax = max(ydat)
    
    gridlength = azmax - azmin

    X = np.linspace(azmin, azmax, meshsize)
    Y = np.linspace(elmax, elmin, meshsize)


    plt.figure(figsize=(16,12))
    plt.subplot(1,2,1)
    plt.imshow(mesh, aspect='equal')
    plt.grid(True)
    plt.plot([x0, x1], [y0, y1], 'ro-')
    plt.plot([x1, x2], [y1, y2], 'bo-')


    #x, y = np.linspace(x0, x1, 40), np.linspace(y0, y1, 40)
    xr = np.linspace(x0, x2, x2-x0)
    #xa, ya = np.linspace(x1, x2, 20), np.linspace(y1, y2, 20)
    yi = np.linspace(y0, y1, x1-x0)
    yj = np.linspace(y1, y2, x2-x1)

    #xr = np.append(x, xa)
    yr = np.append(yi, yj)

    plt.subplot(1,2,2)
    plt.imshow(mesh, aspect='equal', extent=[azmin, azmax, elmin, elmax])
    plt.grid(True)
    plt.plot([X[x0], X[x1]], [Y[y0], Y[y1]], 'ro-')
    plt.plot([X[x1], X[x2]], [Y[y1], Y[y2]], 'bo-')


    zi = mesh[xr.astype(np.int), yr.astype(np.int)]
    zi = scipy.ndimage.map_coordinates(np.transpose(mesh), np.vstack((xr,yr)))

    if norm == True:
        zi = zi/max(zi)
        
    #this version does a radial calculation for cut
    azi = np.linspace(-1*np.sqrt(X[x0]**2+(Y[y0])**2), np.sqrt(X[x2]**2+(Y[y2])**2), len(zi))
    peaks, _ = find_peaks(zi, prominence=prom)
    results_half = peak_widths(zi, peaks, rel_height=rel_height)


    plt.figure(figsize=(16,8))
    plt.plot(azi, zi, label="Cut", lw=4)
    plt.legend(loc='upper left', fontsize=15)
    plt.xlabel('Focal Plane Cut (Radial) (m)')
    plt.ylabel('Normalised Intensity (W)')
    plt.title('blah (blah)')
    
    if rpeaks == True:
        plt.plot(azi[peaks], zi[peaks], "x", label="Peaks", mew=5, ms=10)
        plt.plot(azi[peaks], results_half[1], '_', mew=5, ms=10, 
             label="fwhm label {:3.3}".format(results_half[0][1]*gridlength/meshsize))
        plt.plot(azi[peaks], zi[peaks], "x", mew=5, ms=10,
             label="Peak Sep {:3.3}, {:3.3}".
                 format(azi[peaks][1]-azi[peaks][0], azi[peaks][1]-azi[peaks][2]))
        return azi, zi, peaks, results_half
    else:
        return azi, zi
