import imp, os, glob
import struct
import csv
#from pandas import read_csv
import numpy as np

from numpy import format_float_scientific
import time
from PyQt5 import QtWidgets


def read_file_TEKAFG3000( filename=''):
    #Filename for TFW to be read in from the PC
    if filename != '':
        filelocation = filename
        wfm_magic_name = "TEKAFG3000"
        wfm_version_check = '20050114'
        try:
            #This section is where we open the TFW file as a binary file for python
            with open(filelocation, 'rb') as f:
                desc = {}
                file_size = f.seek(0,2) #size of file
                f.seek(0,0)
                #the header for TFW files is 512 bytes. So we'll read the sub sections to validate the waveform and get the file size
                header = f.read(512)
                #the first section is the 'magic section'
                binary_magic = header[:16]
                magic = struct.unpack( '16c', binary_magic)
                magic = binary_magic.decode('utf-8')
                desc['magic']=magic
                #lets do a quick check to make sure the beginning of the TFW file is correct, more checks can be performed if needed
                #on version, thumbnail or comparing the size is correct.
                if magic[:10] == wfm_magic_name:
                    print('Check 1: This is a valid AFG TFW file')
                else:
                    print('Check 1: This is not a valid AFG TFW file')
                    return None
                #This next section is the version information about the AFG3000. It should read back 20050114
                binary_version = header[16:16+4]
                version = struct.unpack('>i', binary_version)
                version = version[0]
                desc['version']=version
                #This next section is the length of the data, also called 'points'.
                binary_points = header[20:20+4]
                points = struct.unpack('>i', binary_points)
                points = points[0]
                print('Data length: ',points)
                desc['data_length']=points
                waveform_data = f.read()
                binwavefrom = struct.unpack('>'+str(points)+'H', waveform_data)
                #check data length to point size.
                if len(waveform_data) == points*2:  #make sure the points*2 bytes is what you compare s
                    print('Check 2: This wfm data is a valid AFG TFW file')
                    desc['binary_waveform'] = binwavefrom
                    
                else:
                    print('Check 2: This wfm data is not a valid AFG TFW file')
                    return None
                return desc
        except:
            return None

def waveform_to_AFG3251_binary(t, y):
    # max: 16382  (2^14-2)
    absmax = max(abs(min(y)), abs(max(y)))
    y = y/absmax
    half = 8192-1
    y = np.asarray(y*half + half).astype(int)

    x_range = max(t)-min(t)
    freq = round(1/x_range,0)

    return freq, tuple(y)

        

def read_tek_csv(fname, return_x=True, subsample=1):
    sample_period = 0.0
    raw_samples = []
    with open(fname, 'rt',encoding='ascii') as csvfile:
        #s = lambda x: x%subsample
        c = csv.reader(csvfile, delimiter=',')
        
        # Sample period is in cell B2 (1,1)
        for row_num, row in enumerate(c):
            if row_num == 1: # get the sample period
                sample_period = float(row[1])
                break
        for row_num, row in enumerate(c):
            if row_num%subsample == 0:
                raw_samples.append(float(row[4]))
    y = np.array(raw_samples)
    if return_x:
        x = np.array(range(len(y)))*sample_period*subsample
        return [x, y]
    else: 
        return [y]

        

def read_tek_ascii(fname, return_x=True, subsample=1):

    r = read_ascii_scope_files_2d([fname],subsample=1)
    data = r['voltage'] 
    
    

    y = data[0]

    if return_x:

        x = r['time']
        return [x, y]
    else:
        return [y]


def read_tek_csv_files_2d(paths, subsample=1, *args, **kwargs):
    ''' this is anew reader for tek csv files, supposed to work slightly faster than the old one
    the speed gain is due to creating a full-size empty 2d array before starting the reading the files
    optional progress dialog has been commented out for now

    returns:
    dict r
    r['files_loaded'] = files_loaded
    r['header'] = header of the first file
    r['voltage'] = 2d voltage array
    r['time'] = horizontal scale values

    '''

    '''if 'progress_dialog' in kwargs:
        progress_dialog = kwargs['progress_dialog']
    else:
        progress_dialog = QtWidgets.QProgressDialog()'''


    nfiles = len (paths)   

    
    file = paths[0]
    file_text = open(file, "r")
    row = 0
    a = True
    header = {}
    while a:
        file_line = file_text.readline()
        tokens = file_line.split(',')
        if len(tokens[0]):
            header[tokens[0].strip('"')]=(tokens[1],tokens[2])
        else:
            a = False
        
        row +=1

    file_text.close()
    nchans = int(header['Record Length'][0])
    sample_period = float(header['Sample Interval'][0])

    data = np.zeros([nfiles, nchans])
    files_loaded = []
    times = []

    x = np.array(range(nchans))*sample_period*subsample
    
    #QtWidgets.QApplication.processEvents()
    for d, file in enumerate(paths):
        '''if d % 2 == 0:
            #update progress bar only every 10 files to save time
            progress_dialog.setValue(d)
            QtWidgets.QApplication.processEvents()'''
        try:
            file_text = open(file, "r")

            a = True
            row = 0
            for row in range(nchans-3):
                data[d][row]=float(file_text.readline().split(',')[4])
            files_loaded.append(file)
            file_text.close()
        except:
            pass
        
        
        '''if progress_dialog.wasCanceled():
            break'''
    '''QtWidgets.QApplication.processEvents()'''
    r = {}
    r['files_loaded'] = files_loaded
    r['header'] = header
    r['voltage'] = data
    r['time'] = x
    return r


def read_ascii_scope_files_2d(paths, subsample=1, *args, **kwargs):
    ''' this is anew reader for tek csv files, supposed to work slightly faster than the old one
    the speed gain is due to creating a full-size empty 2d array before starting the reading the files
    optional progress dialog has been commented out for now

    returns:
    dict r
    r['files_loaded'] = files_loaded
    r['header'] = header of the first file
    r['voltage'] = 2d voltage array
    r['time'] = horizontal scale values

    '''

    '''if 'progress_dialog' in kwargs:
        progress_dialog = kwargs['progress_dialog']
    else:
        progress_dialog = QtWidgets.QProgressDialog()'''


    nfiles = len (paths)   

    
    file = paths[0]
    header = {}

    file_text = open(file, "r")
    row = 0
    a = True
    horz = []
    for i in range (2):
        file_line = file_text.readline()
        t = file_line.split('\t')[0]
        horz.append( float(t))
       
        row +=1

    file_text.close()
    nchans = 10000 #int(header['Record Length'][0])
    sample_period = round(horz[1]-horz[0],12)

    data = np.zeros([nfiles, nchans])
    files_loaded = []
    times = []

    x = np.array(range(nchans))*sample_period*subsample
    
    #QtWidgets.QApplication.processEvents()
    for d, file in enumerate(paths):
        '''if d % 2 == 0:
            #update progress bar only every 10 files to save time
            progress_dialog.setValue(d)
            QtWidgets.QApplication.processEvents()'''
        try:
            file_text = open(file, "r")

            a = True
            row = 0
            for row in range(nchans-3):
                data[d][row]=float(file_text.readline().split('\t')[1])
            files_loaded.append(file)
            file_text.close()
        except:
            pass
        
        
        '''if progress_dialog.wasCanceled():
            break'''
    '''QtWidgets.QApplication.processEvents()'''
    r = {}
    r['files_loaded'] = files_loaded
    r['header'] = header
    r['voltage'] = data
    r['time'] = x
    return r

def write_tek_csv(fname, x,y, params = {}):
    length = len(x)
    sam_interval = x[1]-x[0]
    header = [  ["Record Length",str(length),"Points"],
                ["Sample Interval",'%.8e'% sam_interval,'s']
                
                
             ]

    if len(params):
        header.append(["Experimental parameters", ' ',' '])
        for key in params:
            param = params[key]
            if len(param):
                p_val = str(param['val'])
                if 'unit' in param:
                    p_unit = param['unit']
                else:
                    p_unit = ''
            header.append([str(key), p_val,p_unit])
    try:
        with open(fname, mode='w',newline='') as csvFile:
            writer = csv.writer(csvFile)
            for row in range(len(header)):
                s = header[row]+['%.8e' % item for item in [x[row],y[row]]]
                writer.writerow(s)
            for row in range(length-len(header)):
                i = row+6
                s = ['','','']+['%.8e' % item for item in [x[i],y[i]]]
                writer.writerow(s)    
        csvFile.close()
        return 0
    except:
        return 1


def read_npy_spectra(filenames):
    spectra = []
    if len(filenames):
        for filename in filenames:
            x, y = read_npy(filename)
            spectra.append(y)
    return spectra, x

def read_npy(filename):
    loaded = np.load(filename)
    keys = list(loaded.keys())
    x, y = loaded[keys[0]]
    return x, y

if __name__ == '__main__':
    

    x = np.asarray(range(100000))*1e-10
    y = np.random.rand(100000)

    write_tek_csv('rand.csv',x,y)
    

