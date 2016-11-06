from mdict_query import IndexBuilder
import os
import json


class Dir(object):
    
    def __init__(self, mdict_dir, config_name = 'config.json'):

        assert(os.path.isdir(mdict_dir))        
        self._mdict_dir = mdict_dir
        self._config_file_base_name = config_name
        self._config = {}
        #check config.json
        self._config_file = os.path.join(mdict_dir, self._config_file_base_name)

        if os.path.exists(self._config_file):
            self._ensure_config_consistency()
            self._load_config()
            self._add_builder()
            pass
        else:
            self._build_index()
            self._make_config()
            self._dump_config()
            self._add_builder()
            pass

    def _add_builder(self):

        for dict in self._config['dicts']:
            dict['builder'] = IndexBuilder(dict['mdx_name'])


    def _load_config(self):

        file_opened = open(self._config_file, 'r', encoding = 'utf-8')
        self._config = json.load(file_opened)
        file_opened.close()


    def _build_index(self):
        
        dict_list = []
        files_in_dir = os.listdir(self._mdict_dir)
        for item in files_in_dir:
            full_name = os.path.join(self._mdict_dir, item)
            print(full_name)
            if os.path.isfile(full_name):
                _filename, _file_extension = os.path.splitext(full_name)
                if _file_extension == '.mdx':
                    _config_single_dic = {
                        'title': '',
                        'description':'',
                        'mdx_name': full_name,
                        'has_mdd': os.path.isfile(_filename + '.mdd')
                        }
                    try:
                        ib = IndexBuilder(full_name)
                    except Exception:
                        continue
                    _config_single_dic['title'] = ib._title
                    _config_single_dic['description'] = ib._description
                    dict_list.append(_config_single_dic)
        self._config['dicts'] = dict_list

    def _make_config(self):
        pass

    def _dump_config(self):

        file_opened = open(self._config_file, 'w', encoding = 'utf-8')
        json.dump(self._config, file_opened, ensure_ascii = False, indent = True)
        file_opened.close()

    #todo: implement ensure consistency
    def _ensure_config_consistency(self):
        pass

Dir('mdx')
