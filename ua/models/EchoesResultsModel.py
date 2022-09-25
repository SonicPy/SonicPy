



import os.path

'''from utilities.utilities import *'''

from utilities.utilities import *
import json
import glob

import time
from deepdiff import DeepDiff


class EchoesResultsModel():
    def __init__(self, mode_ind = 1):
        self._json = None
        
        self.subfolders = []
        self.folder = ''
        self.echoes_p = {}
        self.echoes_s = {}
        self.tof_results_p = {}
        self.tof_results_s = {}
        modes = [ 'fs', 'json']
        self.mode_ind = mode_ind
        self.mode = modes[mode_ind]
        self.project = {}

    def clear(self, mode_ind =1):
        self.__init__(mode_ind=mode_ind)

    def get_folder(self):
        if 'folder' in self.project:
            folder = self.project['folder']
        else:
            folder = ''
        return folder
    
    def get_mode(self):
        mode = ''
        if 'settings' in self.project:
            if 'mode' in self.project['settings']:
                mode = self.project['settings']['mode']
        return mode

    def set_mode(self, mode):
        if not 'settings' in self.project:
            self.project['settings']={}
        self.project['settings']['mode']=mode

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
        
        self.project['folders_sorted'] = folders_sorted

    def get_folders_sorted(self):
        if 'folders_sorted' in self.project:
            folders_sorted = self.project['folders_sorted']
        else:
            folders_sorted = []
            self.project['folders_sorted'] = []
        return folders_sorted

    def get_project_file_name(self):
        
        if self.mode == 'json':
            return self._json

    def open_project(self, fname):
        
        self.clear(self.mode_ind)
        set_ok = self.set_new_project_file_path(fname)
        folder = ''
        if set_ok:
            
            if self.mode == 'json':
                if 'folder' in self.project:
                    folder = self.project['folder']
                    if len(folder):
                        folder = os.path.normpath(folder)
            self.folder = folder
        return set_ok

    def save_project(self):
        set_ok = False
        if self.mode == 'json':
            set_ok = self._save_project_json()
        return set_ok

    def save_project_as(self, filename):
        set_ok = False
        if self.mode == 'json':
            self._json = filename
            set_ok = self._save_project_json()
        return set_ok

    def _save_project_json(self):
        now = time.time()
        self._write_project(self._json,self.project)
        #print('saved in ' + str(time.time()-now) + ' s')

    def set_new_project_file_path(self, fname):
        set_ok = False
        
        if self.mode == 'json':
            set_ok = self._set_new_project_file_path_json(fname)
        return set_ok

    

    def _set_new_project_file_path_json(self, fname):

   
        set_ok = False
        self._json = fname
        if os.path.isfile(fname) and len(fname):
            extension = os.path.basename(fname).split('.')[-1]
            if extension == 'json':
                data = read_result_file(fname)
            elif extension == 'bz':
                data = self._read_project(fname)
            self.project = data

            folder = self.get_folder()
            mode = self.get_mode()
            if len(folder):
                if not len(mode):
                    self.set_mode('discrete_f')

            set_ok = True
        else:
            self._write_project(fname, {})
            set_ok = True
        return set_ok

    def _read_project(self, fname):
        extension = os.path.basename(fname).split('.')[-1]
        data = {}
        if extension == 'json':
            data = read_result_file(fname)
        elif extension == 'bz':
            data = read_result_file_compressed(fname)
        return data

    def _write_project(self, fname, data):
        extension = os.path.basename(fname).split('.')[-1]
     
        if extension == 'json':
            write_data_dict_to_json(fname, data)
        elif extension == 'bz':
            write_data_dict_to_compressed_json(fname, data)
        

    def set_folder(self, folder):
        self.folder = folder
        
        if self.mode == 'json':
            self._set_folder_json(folder)


    def _set_folder_json(self,folder):
        self.project['folder'] = folder


    def set_subfolders(self, subfolders):
        if self.mode == 'fs':
            self._set_subfolders_fs(subfolders)
        
        elif self.mode == 'json':
            self._set_subfolders_json(subfolders)
        

    def _set_subfolders_fs(self, subfolders):
        self.subfolders = subfolders
        
 

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
        
        if self.mode == 'fs':
            deleted = self._delete_echo_fs(filename_waveform, frequency, wave_type)

        elif self.mode == 'json':
            deleted = self._delete_echo_json(filename_waveform, frequency, wave_type)

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
        
        if self.mode == 'fs':
            self._delete_result_fs(clear_info)
        elif self.mode == 'json':
            self._delete_result_json(clear_info)

    

    def _delete_result_json(self, clear_info):
        wave_type = clear_info['wave_type']
        condition = clear_info['condition']
        if condition != None and len(self.project):
            if 'datasets' in self.project:
                if condition in self.project['datasets']:
                    if 'results' in self.project['datasets'][condition]:
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
                    folder = self.get_folder_of_file(fname)
                    
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
        
        if self.mode == 'fs':
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
        subfolder = self.get_folder_of_file(filename_waveform)
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

        
        if self.mode == 'fs':
            self._save_tof_result_fs(output_package)   
        elif self.mode == 'json':
            self._save_tof_result_json(output_package)   

    

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
        self.add_echoe(correlation)   
        if 'filename_waveform' in correlation:
            filename_waveform = os.path.normpath(correlation['filename_waveform'])
            correlation['filename_waveform'] = filename_waveform

        
        if self.mode == 'fs':
            self._save_result_fs(correlation)
        elif self.mode == 'json':
            self._save_result_json(correlation)

    

    def get_extension_of_file(self, file):
        fname = f_ext = os.path.split(file)[-1]
        name = file
        if '.' in fname:
            s = ('.' + fname).split('.')
            f_ext = s[-1]
            name = s[-2]
        else:
            f_ext = ''
            name = fname
        return name, f_ext

    def get_folder_of_file(self, fname):
        mode = self.project['settings']['mode']
        if mode == 'discrete_f':
            folder = os.path.split(fname)[:-1]
            rel_folder = os.path.split(folder[0])[-1]
        elif mode == 'broadband':
            rel_folder, _ = self.get_extension_of_file(fname)
        return rel_folder

    def _save_result_json(self, correlation ):
        wave_type = correlation['wave_type']
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            rel_folder = self.get_folder_of_file(fname)
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
        
        if self.mode == 'fs':
            self._load_tof_results_from_file_fs()
        elif self.mode == 'json':
            self._load_tof_results_from_file_json()

    

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
        
        if self.mode == 'fs':
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
                
                mode = self.project['settings']['mode']
                if mode == 'discrete_f':
                    base_folder = self.get_folder_of_file(saved_path)
                    updated_path = os.path.join(self.folder, base_folder, file_split)
                elif mode == 'broadband':
                    updated_path = updated_path = os.path.join(self.folder, file_split)
                correlation['filename_waveform'] = updated_path
                self.add_echoe(correlation)
                            
            
