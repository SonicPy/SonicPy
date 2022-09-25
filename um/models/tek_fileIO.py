from fileinput import filename
import imp, os, glob
import struct
import csv
#from pandas import read_csv
import numpy as np

from numpy import format_float_scientific
import time
from PyQt5 import QtWidgets


def read_multiple_spectra(filenames, subsample = 1):
    spectra = []
    f = filenames[0]
    X,Y = read_tek_csv(f, return_x=True, subsample=subsample)
    
    for f in filenames:
        Y = read_tek_csv(f, return_x=False, subsample=subsample)
        y = Y
        
        spectra.append(y)
    return spectra, X

def read_multiple_spectra_dict(filenames, subsample = 1 ):

    spectra = []
    f = filenames[0]
    X,Y = read_tek_csv(f, return_x=True, subsample=subsample)
    x = np.asarray(X)
    missing_couner = 1
    missing_waveform = [np.asarray([]),np.asarray([])]
    for d, f in enumerate(filenames):
        
        if f is not None and len(f):
            Y = read_tek_csv(f, return_x=False, subsample=subsample)
            y = np.asarray(Y)
            spectra.append({ 'filename':f,'waveform':[x, y]})
        else:
            spectra.append({ 'filename':'missing_file_'+str(missing_couner),'waveform':missing_waveform})
        
        
    return spectra

def read_2D_spectra_dict(filenames, subsample = 1 ):

    r = None

    fformat, fformat_name = get_file_format(filenames[0])
    #print(filenames[0])
    if fformat == 1:
        r = read_tek_csv_files_2d(filenames, subsample=subsample)
       
    elif fformat == 2:
        r = read_ascii_scope_files_2d(filenames, subsample = subsample)
    
    elif fformat == 4:
        r = read_ascii_scope_files_2d(filenames,subsample=1, separator=',', skip_rows=1, nchans = 200000)
        
    elif fformat == 5:
        r = read_tek_csv_files_2d(filenames,subsample=1, header_columns=2,skip_rows=1,column_shift=0)
    
    '''file  = os.path.split(filenames[0])[-1]
    if '.' in file:
        ext = '.' + file.split('.')[-1]
    else:
        ext = ''

    if ext == '.csv':
        r = read_tek_csv_files_2d(filenames, subsample=subsample)
    elif ext == '':
        r = read_ascii_scope_files_2d(filenames, subsample = subsample)'''
    
    spectra = []
    if r != None:
        for d, f in enumerate(filenames):
            spectra.append({ 'filename':f,'waveform':[r['time'], r['voltage'][d]]})
        
    #print(fformat)
    return spectra

def load_any_waveform_file(filename):

        
        t = np.zeros(1)
        spectrum = np.zeros(1)
        

        fformat, fformat_name = get_file_format(filename)
        if fformat == 1:
            t, spectrum = read_tek_csv(filename, subsample=1)
            #t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        elif fformat == 2:
            t, spectrum = read_tek_ascii(filename, subsample=1)
      
        elif fformat == 4:
            t, spectrum = read_stonybrook_wavestar(filename, subsample=1)
           
        elif fformat == 5:
            t, spectrum = read_gsecars_oscilloscope(filename, subsample=1)

        print(fformat)
        return t,spectrum

def get_file_format( fname):
    '''
    used for determining the file format for the oscilloscope waveform data
    Supported types:
    1. HPCAT tek scope (column 0-3: header, column 4-5: 2-column data)
    2. LANL 2-column, no header
    3. Stonybrook scope (same as 1), returns as 1
    4. Stonybrook wavestar (2-column, one line header)
    5. GSECARS (2-column with full header)

    returns: tuple with file format number 1-n, or -1 if not recognised, and the file format name
    '''

    if len(fname):
        if os.path.isfile(fname):
            file_text = open(fname, "r")
            
            file_line = file_text.readline()
            separator = None
            formats = [ (-1, ''),
                        (1, 'hpcat'),
                        (2, 'lanl'),
                        (4, 'stonybrook'),
                        (5, 'gsecars')
                        ]
            fformat = 0

            if '\t' in file_line:
                # tab separated
                # LANL format
                #separator = '\t'
                #tokens = file_line.split(separator)
                fformat = 2

            elif ',' in file_line:
                header = {}
                # coma separated
                separator = ','    
                tokens = file_line.split(separator)
                
                if len(tokens) == 5:
                    # hpcat format
                    fformat =  1

                elif len(tokens) == 2:

                    if tokens[0].strip() == 's' and tokens[1].strip() == 'Volts':
                        # stonybrook wavestar format
                        fformat =  3
                    
                    # Check if there is a multiline 2-column header (GSECARS)
                    header = {}
                    a = True
                    if len(tokens[0]):
                            header[tokens[0].strip('"').strip()]=(tokens[1].strip())
                    else:
                        a = False
                    row = 1

                    while a:
                        file_line = file_text.readline()
                        tokens = file_line.split(separator)
                        if len(tokens[0])>1:
                            header[tokens[0].strip('"').strip()]=(tokens[1].strip())
                        else:
                            a = False
                        row +=1
                    
                    if "Model" in header:
                        # gsecars format
                        fformat =  4

            file_text.close()

    return formats[fformat]

'''fnames = ['/Users/hrubiak/Downloads/Ultrasonic/3 StonyBrook_Oscilloscope/3 StonyBrook_Oscilloscope_u-300.csv',
           '/Users/hrubiak/Downloads/Ultrasound_XRD_datasets_for_dissemination/Ultrasound_data_for_dissemination_June_2018_Exp4/US/Exp4_25_C_8750_psi/Exp4_25_C_8750_psi_71000_khz',
           '/Users/hrubiak/Downloads/Ultrasonic/3 StonyBrook_Oscilloscope/3 StonyBrook_Oscilloscope_u-300.csv',
           '/Users/hrubiak/Downloads/Ultrasonic/4 StonyBrook_WaveStar/4 StonyBrook_WaveStar_u-060.csv',
           '/Users/hrubiak/Downloads/Ultrasonic/2 GSECARS_transferfunction/2 GSECARS_transferfunction_u600-d673K.csv'
           ]
for fname in fnames:
    fformat = get_file_format(fname)
    print (fname)
    print (fformat)'''

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

def read_gsecars_oscilloscope(fname, return_x=True, subsample=1):
    r = read_tek_csv_files_2d([fname],subsample=1, header_columns=2,skip_rows=1,column_shift=0)
    data = r['voltage'] 
    
    

    y = data[0]

    if return_x:

        x = r['time']
        return [x, y]
    else:
        return [y]


def read_stonybrook_wavestar(fname, return_x=True, subsample=1):
    r = read_ascii_scope_files_2d([fname],subsample=1, separator=',', skip_rows=1, nchans = 200000)
    data = r['voltage'] 
    y = data[0]

    if return_x:

        x = r['time']
        return [x, y]
    else:
        return [y]

def read_tek_csv_files_2d(paths, subsample=1, header_columns = 3, skip_rows = 0, column_shift = 3, *args, **kwargs):
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
        if len(tokens[0])>1:
            val = []

            for v in range(header_columns-1):
                val.append(tokens[v+1].strip())
            header[tokens[0].strip('"')]=tuple(val)
       
        else:
            a = False
        
        row +=1

    file_text.close()
    nchans = int(header['Record Length'][0])
    sample_period = float(header['Sample Interval'][0])

    data = np.zeros([nfiles, nchans])
    files_loaded = []
    times = []

    if column_shift == 0:
        skip_rows = skip_rows + row

    x = np.array(range(nchans))*sample_period*subsample
    
    if skip_rows:
        # this option is used for gsecars format, somtimes you get "1.#INF00e+00" values
        # (for hpcat format skiprows would be 0) 
        checkINF = True
    else:
        # this option may save a few milliseconds?
        #print('hpcat')
        checkINF = False

    data_position = column_shift+1
    for d, file in enumerate(paths):
        '''if d % 2 == 0:
            #update progress bar only every 10 files to save time
            progress_dialog.setValue(d)
            QtWidgets.QApplication.processEvents()'''
        
        
        if len(file):
            file_text = open(file, "r")
            for skip_row in range(skip_rows):
                file_line = file_text.readline()
                
            a = True
            row = 0
            
            if checkINF:
                for row in range(nchans-3):
                    line_str  = file_text.readline()
                    if not '#' in line_str:
                        data[d][row]=float(line_str.split(',')[data_position])
            else:
                for row in range(nchans-3):
                    data[d][row]=float(file_text.readline().split(',')[data_position])
                
            files_loaded.append(file)
            file_text.close()
        
        
        
        '''if progress_dialog.wasCanceled():
            break'''
    '''QtWidgets.QApplication.processEvents()'''
    r = {}
    r['files_loaded'] = files_loaded
    r['header'] = header
    r['voltage'] = data
    r['time'] = x
    return r


def read_ascii_scope_files_2d(paths, subsample=1, separator = '\t',skip_rows = 0, nchans = 10000, *args, **kwargs):
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
    for skip_row in range(skip_rows):
        file_line = file_text.readline()
    for i in range (2):
        file_line = file_text.readline()
        t = file_line.split(separator)[0]
        horz.append( float(t))
       
        row +=1

    file_text.close()
    
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
            if len(file):
                file_text = open(file, "r")
                for skip_row in range(skip_rows):
                    file_line = file_text.readline()
                a = True
                row = 0
                for row in range(nchans-3):
                    data[d][row]=float(file_text.readline().split(separator)[1])
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



