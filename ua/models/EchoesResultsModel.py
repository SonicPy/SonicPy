



import os.path

'''from utilities.utilities import *'''

from utilities.utilities import *
import json
import glob
import h5py
import time
from deepdiff import DeepDiff


class EchoesResultsModel():
    def __init__(self, mode_ind = 2):
        self._json = None
        self._h5py = None
        self.subfolders = []
        self.folder = ''
        self.echoes_p = {}
        self.echoes_s = {}

        self.tof_results_p = {}
        self.tof_results_s = {}

        modes = ['h5py', 'fs', 'json']
        self.mode_ind = mode_ind
        self.mode = modes[mode_ind]

        self.project = {}
        self.folders_sorted = []
  

    def clear(self, mode_ind =2):
        self.__init__(mode_ind=mode_ind)

    def update_settings(self, settings):
        if not 'settings' in self.project:
            self.project['settings'] = {}
        for key in settings:
            self.project['settings'][key] = settings[key]

    def get_settings(self):
        if 'settings' in self.project:
            return self.project['settings']
        else:
            return {}

    def set_folders_sorted(self, folders_sorted):
        self.folders_sorted = folders_sorted

    def get_folders_sorted(self):
        return self.folders_sorted

    def get_project_file_name(self):
        if self.mode == 'h5py':
            return self._h5py
        elif self.mode == 'json':
            return self._json

    def open_project(self, fname):
        
        self.clear(self.mode_ind)
        set_ok = self.set_new_project_file_path(fname)
        folder = ''
        if set_ok:
            if self.mode == 'h5py':
                with  h5py.File(self._h5py, 'a') as h5file:
                    if 'folder' in h5file:
                        folder = h5file['folder'].value
            elif self.mode == 'json':
                if 'folder' in self.project:
                    folder = self.project['folder']
            
            self.folder = os.path.normpath(folder)
        return set_ok

    def save_project(self):
        if self.mode == 'json':
            set_ok = self._save_project_json()

    def _save_project_json(self):
        now = time.time()
        write_data_dict_to_json(self._json,self.project)
        print('saved in ' + str(time.time()-now) + ' s')

    def set_new_project_file_path(self, fname):
        set_ok = False
        if self.mode == 'h5py':
            set_ok = self._set_new_project_file_path_h5py(fname)
        elif self.mode == 'json':
            set_ok = self._set_new_project_file_path_json(fname)
        return set_ok

    def _set_new_project_file_path_h5py(self, fname):

   
        set_ok = False
        self._h5py = fname
        with  h5py.File(self._h5py, 'a') as h5file:
            set_ok = True
        return set_ok

    def _set_new_project_file_path_json(self, fname):

   
        set_ok = False
        self._json = fname
        if os.path.isfile(fname) and len(fname):
            data = read_result_file(fname)
            self.project = data
            set_ok = True
        else:
            write_data_dict_to_json(fname, {})
            set_ok = True
        return set_ok

    def set_folder(self, folder):
        self.folder = folder
        if self.mode == 'h5py':
            self._set_folder_h5py(folder)
        elif self.mode == 'json':
            self._set_folder_json(folder)

    def _set_folder_h5py(self,folder):
        with  h5py.File(self._h5py, 'a') as h5file:
            if 'folder' in h5file:
                folder_old = h5file['folder'].value
                if folder != folder_old:
                    del h5file['folder']
                    h5file['folder'] = folder
            else:
                h5file['folder'] = folder

    def _set_folder_json(self,folder):
        self.project['folder'] = folder


    def set_subfolders(self, subfolders):
        if self.mode == 'fs':
            self._set_subfolders_fs(subfolders)
        elif self.mode == 'h5py':
            self._set_subfolders_h5py(subfolders)
        elif self.mode == 'json':
            self._set_subfolders_json(subfolders)
        

    def _set_subfolders_fs(self, subfolders):
        self.subfolders = subfolders
        
    def _set_subfolders_h5py(self, subfolders):
        self.subfolders = subfolders
        
        with  h5py.File(self._h5py, 'a') as h5file:
            for subfolder in subfolders:
                if not subfolder in h5file:
                    h5file.create_group(subfolder)

    def _set_subfolders_json(self, subfolders):
        self.subfolders = subfolders
        
        if not 'datasets' in self.project:
            self.project['datasets'] = {}
        for subfolder in subfolders:
            if not subfolder in self.project['datasets']:
                self.project['datasets'][subfolder] = {'P':{},'S':{},'results':{}}


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
        if self.mode == 'h5py':
            deleted = self._delete_echo_h5py(filename_waveform, frequency, wave_type)
        elif self.mode == 'fs':
            deleted = self._delete_echo_fs(filename_waveform, frequency, wave_type)

        elif self.mode == 'json':
            deleted = self._delete_echo_json(filename_waveform, frequency, wave_type)

        return deleted

    def _delete_echo_h5py(self, filename_waveform, frequency, wave_type):
        deleted = False

        #  delete in hdf5
        saved_path = os.path.normpath(filename_waveform)
        base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
            
        folder = base_folder + '/' + wave_type
        with h5py.File(self._h5py, 'r') as h5file:
            exists = folder in h5file

            if exists:
                search_str = str(round(frequency*1e-6,1))+'_MHz.json'
                res_files = list(h5file[folder].keys())
        for file in res_files:
            if search_str in file:
                file_for_deletion = folder + '/' + file
                
                with h5py.File(self._h5py, 'a') as h5file:
                    if file_for_deletion in h5file:
                        del h5file[file_for_deletion]
                
                    deleted = True
                if wave_type == "P":
                    if filename_waveform in self.echoes_p:
                        del self.echoes_p[filename_waveform]
                elif wave_type == "S":
                    if filename_waveform in self.echoes_s:
                        del self.echoes_s[filename_waveform]
        return deleted

    def _delete_echo_json(self, filename_waveform, frequency, wave_type):
        deleted = False

        #  delete in json
        saved_path = os.path.normpath(filename_waveform)
        base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
            
        folder = base_folder + '/' + wave_type
        
        exists = wave_type in self.project['datasets'][base_folder]

        if exists:
            search_str = str(round(frequency*1e-6,1))+'_MHz.json'
            res_files = list(self.project['datasets'][base_folder][wave_type].keys())

            for file in res_files:
                if search_str in file:
                    file_for_deletion = file
                    
                    
                    if file_for_deletion in self.project['datasets'][base_folder][wave_type]:
                        del self.project['datasets'][base_folder][wave_type][file_for_deletion]
                    
                        deleted = True
                    if wave_type == "P":
                        if filename_waveform in self.echoes_p:
                            del self.echoes_p[filename_waveform]
                    elif wave_type == "S":
                        if filename_waveform in self.echoes_s:
                            del self.echoes_s[filename_waveform]
        return deleted

    def _delete_echo_fs(self, filename_waveform, frequency, wave_type):
        deleted = False

        #  delete in filesystem
        saved_path = os.path.normpath(filename_waveform)
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
                elif wave_type == "S":
                    if filename_waveform in self.echoes_s:
                        del self.echoes_s[filename_waveform]
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
        if self.mode == 'h5py':
            self._delete_result_h5py(clear_info)
        elif self.mode == 'fs':
            self._delete_result_fs(clear_info)
        elif self.mode == 'json':
            self._delete_result_json(clear_info)

    def _delete_result_h5py(self, clear_info):
        wave_type = clear_info['wave_type']
        condition = clear_info['condition']
        cl = clear_info['clear_info']
        # save to file
        if len(cl):
            p_folder =  condition +'/'+ 'results'
            basename = condition + '.' + wave_type + '.json'
            filename = p_folder +'/'+ basename
            with h5py.File(self._h5py, 'a') as h5file:
                exists = filename in h5file
                if exists:
                    del h5file[filename]

    def _delete_result_json(self, clear_info):
        wave_type = clear_info['wave_type']
        condition = clear_info['condition']
        
        basename = condition + '.' + wave_type + '.json'
        filename = basename
        exists = filename in self.project['datasets'][condition]['results']
        if exists:
            del self.project['datasets'][condition]['results'][filename]
            

    def _delete_result_fs(self, clear_info):
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
        elif self.mode == 'json':
            self._save_new_centers_json(optimum, wave_type)

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

    
    def _save_new_centers_json(self, optimum, wave_type):
        # save center opt in the individual MHz files
        filename_waveform = os.path.normpath( optimum['filename_waveform'])
        center = optimum['center_opt']
        freq = optimum['freq']
        subfolder = os.path.split(filename_waveform)[0]
        subfolder = os.path.split(subfolder)[-1]
        folder = subfolder + '/' + wave_type
        basename = os.path.basename(filename_waveform)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
        filename = folder +'/'+basename

        is_file = basename in self.project['datasets'][subfolder][wave_type]
        if is_file:

            data = self.project['datasets'][subfolder][wave_type][basename ]
            
            data['centers'] = center
            data['filename_waveform'] = os.path.normpath( data['filename_waveform'])
            self.project['datasets'][subfolder][wave_type][basename ] = data
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

        if self.mode == 'h5py':
            self._save_tof_result_h5py(output_package)
        elif self.mode == 'fs':
            self._save_tof_result_fs(output_package)   
        elif self.mode == 'json':
            self._save_tof_result_json(output_package)   

    def _save_tof_result_h5py(self, package):
        wave_type = package['wave_type']
        condition = package['cond']
        p_folder = condition +'/results'
        with h5py.File(self._h5py, 'r') as h5file:
            exists = p_folder in h5file
        with h5py.File(self._h5py, 'a') as h5file:
            if not exists:
                h5file.create_group(p_folder)
            basename = condition + '.' + wave_type + '.json'
            path = p_folder + '/'+ basename 
            if path in h5file:
                del h5file[path]
            recursively_save_dict_contents_to_group(h5file, path + '/', package)

    def _save_tof_result_json(self, package):

        wave_type = package['wave_type']
        condition = package['cond']
        
        exists = 'results' in self.project['datasets'][condition]
        if not exists:
            self.project['datasets'][condition]['results'] = {}
        basename = condition + '.' + wave_type + '.json'
        self.project['datasets'][condition]['results'][basename]= package
                        
    def _save_tof_result_fs(self, package):
        
        wave_type = package['wave_type']
        condition = package['cond']
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
                json.dump(package, json_file, indent = 2) 
                json_file.close()
        except:
            print('could not save file: '+ filename)                
 
    def save_result(self, correlation ):
        if 'filename_waveform' in correlation:
            filename_waveform = os.path.normpath(correlation['filename_waveform'])
            correlation['filename_waveform'] = filename_waveform

        if self.mode == 'h5py':
            self._save_result_h5py(correlation)
        elif self.mode == 'fs':
            self._save_result_fs(correlation)
        elif self.mode == 'json':
            self._save_result_json(correlation)

    def _save_result_h5py(self, correlation ):
        wave_type = correlation['wave_type']
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            folder = os.path.split(fname)[:-1]
            rel_folder = os.path.split(folder[0])[-1]
            rel_p_folder = rel_folder +'/'+  wave_type
            with h5py.File(self._h5py, 'r') as h5file:
                rel_exists = rel_p_folder in h5file
            with h5py.File(self._h5py, 'a') as h5file:
                if not rel_exists:
                    h5file.create_group(rel_p_folder)
                data = echo
                basename = os.path.basename(fname)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
                path = rel_p_folder + '/'+ basename +'/'
                if path in h5file:
                    del h5file[path]
                recursively_save_dict_contents_to_group(h5file, path, data)

    def _save_result_json(self, correlation ):
        wave_type = correlation['wave_type']
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            folder = os.path.split(fname)[:-1]
            rel_folder = os.path.split(folder[0])[-1]
            rel_exists = wave_type in self.project['datasets'][rel_folder]
            if not rel_exists:
                self.project['datasets'][rel_folder][wave_type]= {}
            data = echo
            basename = os.path.basename(fname)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
            self.project['datasets'][rel_folder][wave_type][basename] =  data


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
        if self.mode == 'h5py':
            self._load_tof_results_from_file_h5py()
        elif self.mode == 'fs':
            self._load_tof_results_from_file_fs()
        elif self.mode == 'json':
            self._load_tof_results_from_file_json()

    def _load_tof_results_from_file_h5py(self ):  
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                if wave_type == 'P':
                    tof_results = self.tof_results_p
                elif wave_type == 'S':
                    tof_results = self.tof_results_s
                p_folder = subfolder +'/results'
                with h5py.File(self._h5py, 'r') as h5file:
                    exists = p_folder in h5file
                if exists:
                    with h5py.File(self._h5py, 'r') as h5file:
                        res_files = list(h5file[p_folder].keys())
                        for file in res_files:
                            if wave_type+ '.json' in file:
                                if subfolder in file:
                                    data = recursively_load_dict_contents_from_group(h5file, p_folder + '/' +file +'/')
                                    data['cond'] = subfolder
                                    data['wave_type'] = wave_type
                                    tof_results[subfolder] =  data

    def _load_tof_results_from_file_json(self ):  
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                if wave_type == 'P':
                    tof_results = self.tof_results_p
                elif wave_type == 'S':
                    tof_results = self.tof_results_s
                exists = 'results' in self.project['datasets'][subfolder]
                if exists:
                    res_files = list(self.project['datasets'][subfolder]['results'].keys())
                    for file in res_files:
                        if wave_type+ '.json' in file:
                            if subfolder in file:
                                data = self.project['datasets'][subfolder]['results'][file]
                                if 'filename_waveform' in data:
                                    filename_waveform = os.path.normpath(data['filename_waveform'])
                                    data['filename_waveform'] = filename_waveform
                                data['cond'] = subfolder
                                data['wave_type'] = wave_type
                                tof_results[subfolder] =  data

    def _load_tof_results_from_file_fs(self ):  
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
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
        elif self.mode == 'json':
            self._load_echoes_from_file_json()

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

    def _load_echoes_from_file_json(self ):
        '''
        loads stored echoes from hdf5
        '''
        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                if len(self.project['datasets'][subfolder][wave_type])    :
                    res_files = list(self.project['datasets'][subfolder][wave_type].keys())
                    for file in res_files:
                        data = self.project['datasets'][subfolder][wave_type][file]
                        correlation = data
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
                        res_files = list(h5file[rel_folder].keys())
                        for file in res_files:
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
                            
            
