



import os.path
import numpy as np
'''from utilities.utilities import *'''


import json
import glob
import h5py

from deepdiff import DeepDiff


class EchoesResultsModel():
    def __init__(self):
        
        self._h5py = None
        self.subfolders = []
        self.folder = ''
        self.echoes_p = {}
        self.echoes_s = {}

        self.tof_results_p = {}
        self.tof_results_s = {}

        modes = ['h5py', 'fs']
        mode = 0
        self.mode = modes[mode]
  

    def clear(self):
        self.__init__()

    def set_folder(self, folder):
        self.folder = folder
        self._h5py = os.path.join(folder,'mytestfile.hdf5') 
       

    def set_subfolders(self, subfolders):
        self._set_subfolders_h5py(subfolders)

    def _set_subfolders_fs(self, subfolders):
        self.subfolders = subfolders
        
    def _set_subfolders_h5py(self, subfolders):
        self.subfolders = subfolders
        
        with  h5py.File(self._h5py, 'a') as h5file:
            for subfolder in subfolders:
                if not subfolder in h5file:
                    h5file.create_group(subfolder)

    def add_echoe(self, correlation):
        
        wave_type = correlation['wave_type']
        freq = correlation['frequency']
        if wave_type == "P":
            if correlation['filename_waveform'] in self.echoes_p:
                correlations = self.echoes_p[correlation['filename_waveform']]
            else:
                correlations = {}
            correlations[freq] = correlation
            self.echoes_p[correlation['filename_waveform']] = correlations
        elif wave_type == "S":

            if correlation['filename_waveform'] in self.echoes_s:
                correlations = self.echoes_s[correlation['filename_waveform']]
            else:
                correlations = {}
            correlations[freq] = correlation
            self.echoes_s[correlation['filename_waveform']] = correlations

    def delete_echo(self, filename_waveform, frequency, wave_type):
        deleted = False
        

        #  delete in filesystem
        saved_path = os.path.normpath(filename_waveform)
        file_split = os.path.split(saved_path)[-1]
        base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
            
            
        folder = os.path.join(self.folder, base_folder, wave_type)
        exists = os.path.exists(folder)
        if exists:
            json_search = os.path.join(folder,'*'+str(round(frequency*1e-6,1))+'_MHz.json')
            res_files = glob.glob(json_search)
            if len(res_files):
                file_for_deletion = res_files[0]

                os.remove(file_for_deletion)
                deleted = True

                if wave_type == "P":
                    if filename_waveform in self.echoes_p:
                        del self.echoes_p[filename_waveform]
                        #deleted = True
                elif wave_type == "S":
                    if filename_waveform in self.echoes_s:
                        del self.echoes_s[filename_waveform]
                        #deleted = True
                

        return deleted

    def delete_echoes(self, clear_info):
        self.delete_result(clear_info)
        cl = clear_info['clear_info']
        wave_type = clear_info['wave_type']
        condition = clear_info['condition']
        
        if wave_type == 'P':
            if condition in self.tof_results_p:
                del self.tof_results_p[condition]
        elif wave_type == 'S':
            if condition in self.tof_results_s:
                del self.tof_results_s[condition]
        cleared = True
        for c in cl:
            wave_type = c['wave_type']
            frequency = c['frequency']
            fname = c['filename_waveform']

            cleared = self.delete_echo(fname, frequency, wave_type)
        

        return cleared

    def delete_result(self, clear_info):
        wave_type = clear_info['wave_type']
        condition = clear_info['condition']
        cl = clear_info['clear_info']
        # save to file

        if len(cl):
            folder = self.folder

            p_folder = os.path.join(folder, condition, 'results')
            exists = os.path.exists(p_folder)
            if not exists:
                try:
                    os.mkdir(p_folder)
                except:
                    return

            basename = condition + '.' + wave_type + '.json'
            filename = os.path.join(p_folder,basename)

            if os.path.isfile(filename):

                os.remove(filename)
        

    def clear(self):
        self.__init__()

    
    def get_echoes(self):
        return self.echoes_p, self.echoes_s

    def get_echoes_by_condition(self, condition, wave_type='P'):
        echoes = {}
        echoes_out = []
        if wave_type == 'P':
            echoes = self.echoes_p
        elif wave_type == 'S':
            echoes = self.echoes_s
        if len(echoes):
            for fname in echoes:
                echo_f = echoes[fname]
                for echo in echo_f:
                    e = echo_f[echo]
                    #freq = echo['frequency']
                    folder = os.path.split(os.path.split(fname)[0])[-1]
                    if folder == condition:
                        echoes_out.append( e)
        return echoes_out

    def get_results_by_condition(self, condition, wave_type = 'P'):
        results = {}
        tof_results = {}
        if wave_type == 'P':
            tof_results = self.tof_results_p
        elif wave_type == 'S':
            tof_results = self.tof_results_s
        if condition in tof_results:
            results = tof_results[condition]
        return results

    def save_new_centers(self, optimum, wave_type):
        if self.mode == 'h5py':
            self._save_new_centers_h5py(optimum, wave_type)
        elif self.mode == 'fs':
            self._save_new_centers_fs(optimum, wave_type)

    def _save_new_centers_fs(self, optimum, wave_type):
        # save center opt in the individual MHz files
        filename_waveform = optimum['filename_waveform']
        center = optimum['center_opt']
        freq = optimum['freq']
        subfolder = os.path.split(filename_waveform)[0]
        folder = os.path.join(subfolder, wave_type)

        basename = os.path.basename(filename_waveform)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
        filename = os.path.join(folder,basename)

        is_file = os.path.isfile(filename)
        if is_file:
            
            with open(filename) as json_file:
                data = json.load(json_file)
                json_file.close()
                
            write = False
            if not 'centers' in data:
                data['centers']= center
                write = True
            else:
                if DeepDiff(data['centers'], center) != {}:
                    data['centers']= center
                    write = True
            if write:
                with open(filename, 'w') as json_file:
                    json.dump(data, json_file, indent = 2) 
                    
                    json_file.close()

                    echoes_set = {}
                    if wave_type == "P":
                        echoes_set = self.echoes_p
                    elif wave_type == "S":
                        echoes_set = self.echoes_s
                    if filename_waveform in echoes_set:
                        echoes =  echoes_set[filename_waveform]
                        for f in echoes:
                            if echoes[f]['frequency']== freq:
                                echoes[f]['centers'] = center
                        echoes_set[filename_waveform] = echoes
                        

    def _save_new_centers_h5py(self, optimum, wave_type):
        # save center opt in the individual MHz files
        filename_waveform = optimum['filename_waveform']
        center = optimum['center_opt']
        freq = optimum['freq']
        subfolder = os.path.split(filename_waveform)[0]
        subfolder = os.path.split(subfolder)[-1]
        folder = subfolder + '/' + wave_type

        basename = os.path.basename(filename_waveform)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
        filename = folder +'/'+basename

        with h5py.File(self._h5py, 'r') as h5file:
            is_file = filename in h5file
        if is_file:
            with h5py.File(self._h5py, 'r') as h5file:
                data = recursively_load_dict_contents_from_group(h5file, filename +'/')
            write = False
            if not 'centers' in data:
                data['centers']= center
                write = True
            else:
                if DeepDiff(data['centers'], center) != {}:
                    data['centers']= center
                    write = True
            if write:
                with h5py.File(self._h5py, 'a') as h5file:
                    if filename in h5file:
                        del h5file[filename]
                    recursively_save_dict_contents_to_group(h5file, filename +'/', data)
                    echoes_set = {}
                    if wave_type == "P":
                        echoes_set = self.echoes_p
                    elif wave_type == "S":
                        echoes_set = self.echoes_s
                    if filename_waveform in echoes_set:
                        echoes =  echoes_set[filename_waveform]
                        for f in echoes:
                            if echoes[f]['frequency']== freq:
                                echoes[f]['centers'] = center
                        echoes_set[filename_waveform] = echoes
                        
    def save_tof_result(self, package):
        # save rest of the result in a seperate [condition].result.json file
        wave_type = package['wave_type']
        condition = package['condition']
        result = package['result']
        line_plots = package['line_plots']

        # only output the result travel time and the arrow plot line fit 
        output_package = {}
        output_package['result'] = result
        output_package['line_plots'] = line_plots
        output_package['wave_type'] = wave_type
        output_package['cond'] = condition

        # update self:
        if wave_type == 'P':
            tof_results = self.tof_results_p
        elif wave_type == 'S':
            tof_results = self.tof_results_s
        tof_results[condition] = output_package
        

        # save to file
        folder = self.folder

        p_folder = os.path.join(folder, condition, 'results')
        exists = os.path.exists(p_folder)
        if not exists:
            try:
                os.mkdir(p_folder)
            except:
                return

        basename = condition + '.' + wave_type + '.json'
        filename = os.path.join(p_folder,basename)
        try:
            with open(filename, 'w') as json_file:
                json.dump(output_package, json_file, indent = 2) 

                json_file.close()
        except:
            print('could not save file: '+ filename)                
 
    def save_result(self, correlation ):
        if self.mode == 'h5py':
            self._save_result_h5py(correlation)
        elif self.mode == 'fs':
            self._save_result_fs(correlation)

    def _save_result_h5py(self, correlation ):
        wave_type = correlation['wave_type']
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            folder = os.path.split(fname)[:-1]
            rel_folder = os.path.split(folder[0])[-1]
            rel_p_folder = rel_folder +'/'+  wave_type
            with h5py.File(self._h5py, 'a') as h5file:
                rel_exists = rel_p_folder in h5file
            if not rel_exists:
                with h5py.File(self._h5py, 'a') as h5file:
                    h5file.create_group(rel_p_folder)
            data = echo
            basename = os.path.basename(fname)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
            with h5py.File(self._h5py, 'a') as h5file:
                path = rel_p_folder + '/'+ basename +'/'
                if path in h5file:
                    del h5file[path]
                recursively_save_dict_contents_to_group(h5file, path, data)

                dd = recursively_load_dict_contents_from_group(h5file,path)
                print(dd)

    def _save_result_fs(self, correlation ):
        wave_type = correlation['wave_type']
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            folder = os.path.split(fname)[:-1]
            p_folder = os.path.join(*folder, wave_type)
            exists = os.path.exists(p_folder)
            if not exists:
                try:
                    os.mkdir(p_folder)
                except:
                    return
            data = echo
            basename = os.path.basename(fname)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
            filename = os.path.join(p_folder,basename)
            with open(filename, 'w') as json_file:
                json.dump(data, json_file, indent = 2) 
                json_file.close()

    def load_tof_results_from_file(self ):

        loaded_package = {}
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                # update self:
                if wave_type == 'P':
                    tof_results = self.tof_results_p
                elif wave_type == 'S':
                    tof_results = self.tof_results_s

                json_search = os.path.join(self.folder, subfolder,'results','*.'+ wave_type+ '.json')
                res_files = glob.glob(json_search)
                if len(res_files):
                    for res in res_files:
                        if subfolder in res:

                            with open(res) as json_file:
                                data = json.load(json_file)
                                
                                json_file.close()
                            data['cond'] = subfolder
                            data['wave_type'] = wave_type
                            
                            tof_results[subfolder] =  data

    def load_echoes_from_file(self ):
        if self.mode == 'h5py':
            self._load_echoes_from_file_h5py()
        elif self.mode == 'fs':
            self._load_echoes_from_file_fs()

    def _load_echoes_from_file_fs(self ):
        '''
        deprecated
        loads stored echoes from json files in separate folders
        '''
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                folder = os.path.join(self.folder, subfolder, wave_type)
                exists = os.path.exists(folder)
                if exists:
                    json_search = os.path.join(folder,'*.json')
                    res_files = glob.glob(json_search)
                    for file in res_files:
                        with open(file) as json_file:
                            data = json.load(json_file)
                            correlation = data
                            json_file.close()
                            self._add_echo_by_dict(correlation)



    def _load_echoes_from_file_h5py(self ):
        '''
        loads stored echoes from hdf5
        '''
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                rel_folder = subfolder + '/' + wave_type
                with h5py.File(self._h5py, 'r') as h5file:
                    rel_exists = rel_folder in h5file
                if rel_exists:
                    with h5py.File(self._h5py, 'r') as h5file:
                        res_files = list(h5file[rel_folder].keys())
                    for file in res_files:
                        with h5py.File(self._h5py, 'r') as h5file:
                            data = recursively_load_dict_contents_from_group(h5file, rel_folder + '/' +file +'/')
                            correlation = data
                            self._add_echo_by_dict(correlation)
                          
    
    def _add_echo_by_dict(self, correlation):
        if 'wave_type' in correlation:
            wave_type = correlation['wave_type']
            if wave_type == wave_type:
                if 'filename_waweform' in correlation:
                    saved_path = correlation['filename_waweform']
                elif 'filename_waveform' in correlation:
                    saved_path = correlation['filename_waveform']
                else:
                    return
                saved_path = os.path.normpath(saved_path)
                file_split = os.path.split(saved_path)[-1]
                base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
                updated_path = os.path.join(self.folder, base_folder, file_split)
                correlation['filename_waveform'] = updated_path
                self.add_echoe(correlation)
                            
            
def save_dict_to_hdf5(dic, filename):
    """
    ....
    """
    with h5py.File(filename, 'a') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)

def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (float,int)):
            item = np.float64(item)
        if isinstance(item,(list)):
            item = np.asarray(item, dtype=np.float64)
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            print(item)
            raise ValueError('Cannot save %s type'%type(item))

def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            val = item[()]
            if isinstance(val,(np.ndarray)):
                val = list(val)
            ans[key] = val
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans