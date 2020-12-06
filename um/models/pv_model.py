

import  time, logging, os, struct, sys, copy

from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import queue 
from functools import partial
import json
from um.models.pvServer import pvServer


class PV(QObject):
    
    value_changed_signal = pyqtSignal(str, list)
    def __init__(self, name='', settings=''):
        super().__init__()
        if name == '':
            return
        self._pv_name=name

        if 'desc' in settings:
            self._description = settings['desc']
        if 'val' in settings:
            self._val = settings['val']
        if 'param' in settings:
            types ={'s':str, 'i':int, 'f':float, 'b':bool, 'l':list, 'dict':dict, 'pv':type(PV)}
            self._type = types[settings['param']['type']]
            if self._type == type(PV):
                pass
            if self._type == list:
                self._items = settings['list']
            if self._type == int or self._type == float:
                if 'val_scale' in settings:
                    self._val_scale = self._val_scale = settings['val_scale']
                else : self._val_scale = 1
        if 'methods' in settings:
            if 'get' in settings['methods']:
                self._get_enabled = settings['methods']['get']
            else:
                self._get_enabled = True
            if 'set' in settings['methods']:
                self._set_enabled = settings['methods']['set']
            else:
                self._set_enabled = True
        else:
            self._get_enabled = True
            self._set_enabled = True
        if 'increment' in settings:
            self._increment = settings['increment']
        if 'min' in settings:
            self._min = settings['min']
        if 'max' in settings:
            self._max = settings['max']    
        if 'format' in settings:
            self._format = settings['format']   
        else: self._format = ''
        if 'unit' in settings:
            self._unit = settings['unit']
        else: self._unit = ''



    def __str__(self):
        return self._pv_name
    

class pvModel(QThread):

    # TODO add autosave_settings file support. autosave file would list pvs that need saving.
    # those pvs would be saved when changed and loaded when running __init__

    model_value_changed_signal = pyqtSignal(dict)
    num_pvs = 0
    def __init__(self, parent):
        super().__init__(parent)
        self.my_queue = queue.Queue()
        self.pv_server = pvServer()

        # may use later for synchronous get:
        # self.get_queue = queue.Queue()
        self.instrument = ''
        self.settings_file_tag =''

        self.connected = False
        self.offline = False
        
        self.valid_types = [str, int, float, bool, dict]
        self.validators ={'s':str, 'i':int, 'f':float, 'b':bool, 'l':str, 'dict':dict}

        self.pvs = {}

        ## device speficic:
        
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = { }

        '''
        Example:
        self.tasks = {'start_freq': 
                                {'desc': 'Start (MHz)', 'val':5.0, 'increment':0.5,'min':1,'max':50 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'type':'f'}},
                                ...
                     }
        '''
        

        '''
        child class needs to call:
        self.create_pvs(self.tasks)
        '''

        
        self.start()

        
        

    def clear_queue(self):
        q = self.my_queue
        with q.mutex:
            q.queue.clear()

    def get_tasks(self):
        return self.tasks


    def create_pvs(self, tasks):

        for tag in tasks:
            self.num_pvs = self.num_pvs + 1
            
            task = tasks[tag]
            self.create_pv(tag, task)
   
    def create_pv(self, tag, task):
        pv_name = self.instrument + ':'+tag
        new_pv = PV(pv_name,task)
        
        for method in ['set', 'get']:
            #if task['methods'][method]:
            private_attr ='_'+method+'_'+ tag
            has_private = hasattr(self, private_attr)
            if not has_private:
                
                self._create_default_private_method(method, tag)
            has_private = hasattr(self, private_attr)
            if not has_private:
                print('failed to create "'+ private_attr+ '" method')
            if has_private:
                attr = method+'_task'
                func = self.__getattribute__(attr)
                params = task['param']
                public_method = partial(func, method, tag, params)
                setattr(new_pv,method,public_method)

        pv_name = self.instrument + ':'+tag
        if self.instrument != '':
            self.pv_server.set_pv(pv_name, new_pv)
        self.pvs[tag]=new_pv

    def _default_set_task(self,tag, val):
        self.pvs[tag]._val = val
        
        #print('set: '+ tag+ ' = ' + str(val))

    def _default_get_task(self, tag):
        val = self.pvs[tag]._val
        #print('set: '+ tag+ ' = ' + str(val))
        return val

    def _create_default_private_method(self, method, tag):
        attr = '_'+method+'_'+ tag
        if method == 'set':
            func = partial(self._default_set_task,tag)
        elif method == 'get':
            func = partial(self._default_get_task,tag)

        setattr(self, attr, func)
       
        #print('create private method: _' + method+ '_'+ tag + ' ('+self.instrument+')') 

    def get_task(self,  mode, task, get_params):
        
        task_str = mode+'_'+task
        self.my_queue.put({'task_name': task, 'mode': mode})
        
       

    def set_task(self,  mode, task, desc_params, param_in):
        pv = self.pvs[task]
        valid, params_out = self.validate_params(desc_params, param_in)
        # if parameters have been validated they should be safe to send to device
        if valid:
            task_str = mode+'_'+task
            queue_item = {'task_name': task, 'mode': mode, 'param':params_out}
            #print('put in queue: ' + str(params_out))
            self.my_queue.put(queue_item)
            #print (queue_item)

    def validate_params(self, desc_param, param_in):
        # here is the validator for the param_in
        #print('param_in: ' + str(param_in))
        valid = True
        param_out = None
        param_type = type(param_in)
        #print(param_type)
        valid_type = type(param_in) in self.valid_types
        
        param=desc_param
        if valid_type:
            #print ('valid_type')
            expected_type = self.validators[param['type']]
            param_out = param_in
            if (expected_type == int and type(param_in) == float):
                #print('expected_type')
                param_val = expected_type(param_in)
                param_type  = expected_type
            if param_type != expected_type:
                
                valid = False
        #print( str(valid) + ', ' + str(param_out))
        return valid, param_out
            
    def exit(self):
        if self.isRunning():
            self.my_queue.put({'task_name': 'exit'})
        
    def run(self):
        self.go= True
        # do stuff
        while self.go:
            task = self.my_queue.get()
            #print('task in queue: ' + str(task))
            
            if 'task_name' in task:
                task_name = task['task_name']
                if task_name == 'exit':
                    self._exit_task()
                    self.go = False
                else:
                    mode = task['mode']
                    attr = '_'+mode+'_'+task_name
                    
                    if hasattr(self, attr):
                        func = self.__getattribute__(attr)
                        if mode == 'set':
                            param = task['param']
                            
                            # param must be validated prior to here !
                            try:
                                func(param)
                            except:
                                print('set failed: '+task_name)
                            self.pvs[task_name]._val = param
                            self.pvs[task_name].value_changed_signal.emit(task_name,[param])
                            #print('emit '+ str(task_name) + ', '+ str(param))
                            
                        elif mode == 'get':
                            #print('get... try:  '+ str(task_name))
                            try:
                                ans = func()
                            except:
                                #print('get failed: '+task_name)
                                ans = None
                            #print('get succeeded')
                            # asynchronously send reply
                            if ans is not None:
                                if type(ans) is not dict:
                                    #print(ans)
                                    pass
                                self.pvs[task_name]._val = ans
                                self.pvs[task_name].value_changed_signal.emit(task_name,[ans])
                                #self.get_queue.put(ans)
        #print('Exited thread')

    def save_settings(self, settings_list, filename):
        data_out = self.get_settings(settings_list)

        try:
            with open(filename) as f:
                openned_file = json.load(f)

                tag = self.settings_file_tag
                if tag in openned_file:
                    openned_file[tag] = data_out[tag]
                    data_out = openned_file
        except:
            pass
        
        try:
            with open(filename, 'w') as outfile:
                json.dump(data_out, outfile, sort_keys=True, indent=4)
                outfile.close()
                #print(data_out)
        except:
            pass

    def get_settings(self, settings_list):
        data = {}
        
        for setting in settings_list:
            pv = self.pvs[setting]
            val = pv._val
            
            t = pv._type
            
            data[setting] = val
        
        tag = self.settings_file_tag
        data_out = {tag:data}
        return data_out
        

    def load_settings(self, filename):
        try:
            with open(filename) as f:
                openned_file = json.load(f)

                tag = self.settings_file_tag
                if tag in openned_file:
                    settings = openned_file[tag]
                    return settings
        except:
            pass
        return None

    

    def _exit_task(self):
        pass