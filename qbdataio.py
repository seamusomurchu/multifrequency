#! /usr/bin/python2.7
import numpy as np
import pandas as pd
import glob
import re
import os
from operator import itemgetter
import csv

"""Program for formating grasp and/or modal files
grasp header explained = https://ftp.space.dtu.dk/pub/ticra

to add multiple grasp files in intensity
"""

def getgraspinfo(fname):
	#find horn num from input file THIS DEPENDS ON WHETHER THE INPUT FILES ARE NAMED CORRECTLY
	fname2 = re.findall('([^/]+$)', fname)
	fname2 = re.findall(r'\d+', str(fname2))
	print("fname2  info = ", fname2, len(fname2), type(fname2))

	infile = open(fname,'r')

	freqindex = 20
	iktype = 20
	iparams = 20
	ixiy_index = 20
	GRASPgridarea = 20
	GRASPpixels = 20
	datastart = 20
	for i in range(20):
		temp = infile.readline()
		print(i, temp)

		if 'FREQUENCIES [GHz]:' in temp:
			freqindex = i + 1
			print(freqindex)

		if i == freqindex:
			frequency = temp
			print(frequency)

		if '++++' in temp:			#this line catches the end of header by finding '++++'
			print('found +++', i)
			headerend = i
			iktype = i + 1
			iparams = i + 2
			ixiy_index = i + 3
			GRASPgridarea = i + 4
			GRASPpixels = i + 5
			datastart = i + 6

		#some of these will require operations
		if i == iktype:
			ktype = temp
		if i == iparams:
			param = temp	
			params = [float(s) for s in param.split()]
			params = np.asarray(params)
		if i == ixiy_index:
			ixiy = temp
			ixiyparam = [float(s) for s in ixiy.split()]
			ixiyparam = np.asarray(ixiyparam)
			
		if i == GRASPgridarea:		#sets grid area into array
			gridarea = temp 
			print("grid area", gridarea)                
			dims = [float(s) for s in gridarea.split()]
			dims = np.asarray(dims)
			print("dimensions", dims[0],dims[2])
		if i == GRASPpixels:
			gpix = temp
			pdims = [float(s) for s in gpix.split()]
			pdims = np.asarray(pdims)

	return frequency, dims, pdims, ktype, params, ixiyparam, datastart

def gdataform(dims, pdims, datastart, fname):
	#number of 'pixel' points from datafile
	nx = pdims[0]	
	ny = pdims[1]

	xmin = dims[0]
	xmax = dims[2]
	ymin = dims[1]
	ymax = dims[3]

	xx = np.linspace(xmin,xmax,nx)
	yy = np.linspace(ymin,ymax,ny) 

	#could optimise this by just adding xx and yy to all_data
	X,Y = np.meshgrid(xx,yy)
	pts = np.c_[Y.ravel(), X.ravel()] # technically backwards but produces correct format 5/03/19

	datalen = len(xx)*len(yy)
	zarr = np.zeros(int(datalen))
	zarr = np.asarray(zarr)
	
	print("datastart", datastart, "fname, ", fname)
	data = np.loadtxt(fname, skiprows=datastart) #choose value dynamically... need to reshape this first, its ruining comb currently

	#this puts data from file into array. could be optimsed by reading straight from file (data)
	data_array = ([])

	for i in data:
		data_array.append(i) 
	data_array = np.asarray(data_array)

	print("data_array info ", data_array[0,0:2], data_array.shape)

	#do calculations for amp and phase
	ampX = ([])
	phaX = ([])
	ampY = ([])
	phaY = ([])
	ampZ = ([])
	phaZ = ([])
	
	print("len data array", len(data_array))

	for i in range(len(data_array)):
		
		ampXvar = np.sqrt(data_array[i,0]**2 + data_array[i,1]**2) 
		ampX.append(ampXvar)

		phaXvar = np.arctan2(data_array[i,1],data_array[i,0])
		phaX.append(phaXvar)

		ampYvar = np.sqrt(data_array[i,2]**2 + data_array[i,3]**2) 
		ampY.append(ampYvar)

		phaYvar = np.arctan2(data_array[i,3],data_array[i,2])
		phaY.append(phaYvar)
		
		ampZvar = np.sqrt(data_array[i,4]**2 + data_array[i,5]**2) 
		ampZ.append(ampZvar)

		phaZvar = np.arctan2(data_array[i,5],data_array[i,4])
		phaZ.append(phaZvar)

	#this could be optimised by leaving as a list before creating data array
	ampX = np.asarray(ampX)	
	phaX = np.asarray(phaX)
	ampY = np.asarray(ampY)
	phaY = np.asarray(phaY)
	ampZ = np.asarray(ampZ)
	phaZ = np.asarray(phaZ)

	#Put individual arrays into one large array
	all_data = np.array([ampX,phaX,ampY,phaY,ampZ,phaZ])

	#transpose array
	all_data = all_data.T
	
	print("all_data shape", all_data.shape)
	print("pts shape", pts.shape)
	print("zarr", zarr.shape)
	
	#reformat xya to include zero arrays to match MODAL style
	#xya = np.vstack((zarr,xya))
	zarrs = np.asarray((zarr,zarr)).T

	#horizontally stack xy location array with data array
	comb_data = np.hstack((pts,all_data))
	comb_data = np.hstack((zarrs,comb_data))
	comb_data = np.hstack((comb_data, data_array))
	#print "all_data = ", all_data, all_data.shape
	print("comb data = ", comb_data, comb_data.shape)
	
	#pause development here and work on grid area output
	return nx, ny, xmin, xmax, ymin, ymax, comb_data

def PandaGraspWrite(comb_data, freq, graspoutputrep, fname, hnum):
    #test comb_data shape
    freq = float(freq)
    freq = format(freq, '3.0f')
    print(type(comb_data), type(freq), type(graspoutputrep), type(fname), type(hnum))
    #setup dict
    comb_dict = {
        'Xind': comb_data[:,0],
        'Yind': comb_data[:,1],
        'Ypos': comb_data[:,2],
        'Xpos': comb_data[:,3],
        'Xamp': comb_data[:,4],
        'Xpha': comb_data[:,5],
        'Yamp': comb_data[:,6],
        'Ypha': comb_data[:,7],
        'Zamp': comb_data[:,8],
        'Zpha': comb_data[:,9],
        'Freq': freq,
        'Hnum': hnum,
        'Rex' : comb_data[:, 10],
        'Imx' : comb_data[:, 11],
        'Rey' : comb_data[:, 12],
        'Imy' : comb_data[:, 13],
        'Rez' : comb_data[:, 14],
        'Imz' : comb_data[:, 15]
    }

#     freqstr = float(freq)
#     freqstr = format(freqstr, '3.0f')
    freqstr = str(freq)
    #create dataframe
    #NB have to swap Xpos & Ypos columns to match MODAL format
    df = pd.DataFrame(comb_dict, columns=['Xind', 'Yind', 'Ypos', 'Xpos', 'Xamp', 'Xpha', 'Yamp', 'Ypha', 'Zamp', 'Zpha', 'Freq', 'Hnum',
										'Rex', 'Imx', 'Rey', 'Imy', 'Rez', 'Imz'])
    print(df)
    df.to_csv(graspoutputrep+fname+'_'+freqstr+'_GHz_Mstyle.qb', sep='\t', index=False, float_format='%.9e')
    return

def DataIOMain(filename):
	# output location, use second for multi frequency analysis
	graspoutputrep = "/home/james/files4CSFPA/Fromqbdataio/"
	#get info from grasp file
	freq, dims, pdims, ktype, params, ixiyparam, datastart = getgraspinfo(filename)
	#get info from those returned paramters ###I'm sure I had a reason for this
	nx, ny, xmin, xmax, ymin, ymax, comb_data = gdataform(dims, pdims, datastart, filename)
	#modify filename for saving - can probably simplify and delete these lines
	fname2 = os.path.basename(filename)
	fname2 = os.path.splitext(fname2)[0]
	#write data with filename
	PandaGraspWrite(comb_data, graspoutputrep, fname2)
	
	return

def MultiMain():
	#grasp grd in files
	inrep = '/home/james/multifreqfiles/MultiFreqFilesCF1/'
	files = sorted(glob.glob(inrep+'*.grd'))
	print('read', len(files), 'files')
	#output location of MODAL style files
	orep = '/home/james/multifreqfiles/outfiles/'
	for f in files:
		print("file path: ", f)
		fname = os.path.basename(f)
		fname = os.path.splitext(fname)[0]
		print("file", fname)
		#basically call qbdataio functions and output to folder
		freq, dims, pdims, ktype, params, ixiyparam, datastart = getgraspinfo(f)
		nx, ny, xmin, xmax, ymin, ymax, comb_data = gdataform(dims, pdims, datastart, f)
		PandaGraspWrite(comb_data, orep, fname)
		
	return	
		
def MultiHornMain(inrep, outrep):
    #grasp grd in files
    files = sorted(glob.glob(inrep+'*.grd'))
    print('read', len(files), 'files')
    #output location of MODAL style files
    for f in files:
        #print("file path: ", f)
        fname = os.path.basename(f)
        #fname = os.path.splitext(fname)[0]
        fname = os.path.splitext(fname)
        #print("file", fname)
        hornnum = re.search(r'\d+', fname[0]).group(0)
        #basically call qbdataio functions and output to folder
        freq, dims, pdims, ktype, params, ixiyparam, datastart = getgraspinfo(f);
        #print("horn num", hornnum, type(hornnum))
        #print("freq info ", freq, type(freq))
        #print("filename, fname: ", fname[0], type(fname[0]))
        nx, ny, xmin, xmax, ymin, ymax, comb_data = gdataform(dims, pdims, datastart, f)
        PandaGraspWrite(comb_data, freq, outrep, fname[0], hornnum)

    return		

