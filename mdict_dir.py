from mdict_query import IndexBuilder
import os
import json


class Dir(object):
    
    def __init__(self, mdict_dir):

        assert(os.path.isdiir(mdict_dir))        
        self._mdict_dir = mdict_dir
        self._config = {}
        #check config.json
        self._config_file = os.path.join(mdict_dir, 'config.json')

        if os.path.exists(self._config_file):
            self._ensure_config_consistency()
            self._load_config()
        else:
            self._build_index()
            self._make_config()
            self._dump_config()


    def _build_index(self):
        
        files_in_dir = os.listdir(self._mdict_dir)
        for item in files_in_dir:
            absolute_dir = os.path.join(self._mdict_dir, item)
            if os.path.isfile(absolute_dir):
                pass



    #def _make_config(self):
    #    pass


    #def _dump_config(self):
    #    pass