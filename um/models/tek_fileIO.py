import struct
import csv
#from pandas import read_csv
import numpy as np

from numpy import format_float_scientific




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

def read_tek_csv(fname, return_x=True, subsample=1):
    sample_period = 0.0
    raw_samples = []
    with open(fname, 'rt',encoding='ascii') as csvfile:
        s = lambda x: x%subsample
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



def write_tek_csv(fname, x,y):
    length = len(x)
    sam_interval = x[1]-x[0]
    header = [  ["Record Length",str(length),"Points"],
                ["Sample Interval",'%.8e'% sam_interval,'s'],
                ["Trigger Point",0,"Samples"],
                ["Record Length",'%.8e' % 0.0,'s'],
                ['','',''],
                ["Horizontal Offset", '%.8e'% 0.0,'s'],
                ]
    try:
        with open(fname, mode='w',newline='') as csvFile:
            writer = csv.writer(csvFile)
            for row in range(6):
                s = header[row]+['%.8e' % item for item in [x[row],y[row]]]
                writer.writerow(s)
            for row in range(length-6):
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
    

