###test
from readmdict import MDX, MDD
from struct import pack, unpack
from io import BytesIO
import re
import sys
import os
import sqlite3
import json

# zlib compression is used for engine version >=2.0
import zlib
# LZO compression is used for engine version < 2.0
try:
    import lzo
except ImportError:
    lzo = None
    #print("LZO compression support is not available")

# 2x3 compatible
if sys.hexversion >= 0x03000000:
    unicode = str


class IndexBuilder(object):
    #todo: enable history
    def __init__(self, fname, encoding = "", passcode = None, force_rebuild = False, enable_history = False):
        self._mdx_file = fname
        self._mdd_file = ""
        self._encoding = ''
        self._stylesheet = {}
        self._title = ''
        self._description = ''
        _filename, _file_extension = os.path.splitext(fname)
        assert(_file_extension == '.mdx')
        assert(os.path.isfile(fname))
        self._mdx_db = _filename + ".mdx.db"
        # make index anyway
        if force_rebuild:
            self._make_mdx_index(self._mdx_db)
            if os.path.isfile(_filename + '.mdd'):
                self._mdd_file = _filename + ".mdd"
                self._mdd_db = _filename + ".mdd.db"
                self._make_mdd_index(self._mdd_db)

        if os.path.isfile(self._mdx_db):
            #read from META table
            conn = sqlite3.connect(self._mdx_db)
            #cursor = conn.execute("SELECT * FROM META")
            cursor = conn.execute("SELECT * FROM META WHERE key = \"encoding\"")
            for cc in cursor:
                self._encoding = cc[1]
            cursor = conn.execute("SELECT * FROM META WHERE key = \"stylesheet\"")
            for cc in cursor:
                self._stylesheet = json.loads(cc[1])

            cursor = conn.execute("SELECT * FROM META WHERE key = \"title\"")
            for cc in cursor:
                self._title = cc[1]

            cursor = conn.execute("SELECT * FROM META WHERE key = \"description\"")
            for cc in cursor:
                self._description = cc[1]

            #for cc in cursor:
            #    if cc[0] == 'encoding':
            #        self._encoding = cc[1]
            #        continue
            #    if cc[0] == 'stylesheet':
            #        self._stylesheet = json.loads(cc[1])
            #        continue
            #    if cc[0] == 'title':
            #        self._title = cc[1]
            #        continue
            #    if cc[0] == 'title':
            #        self._description = cc[1]
        else:
            self._make_mdx_index(self._mdx_db)

        if os.path.isfile(_filename + ".mdd"):
            self._mdd_file = _filename + ".mdd"
            self._mdd_db = _filename + ".mdd.db"
            if not os.path.isfile(self._mdd_db):
                self._make_mdd_index(self._mdd_db)
        pass
    

    def _replace_stylesheet(self, txt):
        # substitute stylesheet definition
        txt_list = re.split('`\d+`', txt)
        txt_tag = re.findall('`\d+`', txt)
        txt_styled = txt_list[0]
        for j, p in enumerate(txt_list[1:]):
            style = self._stylesheet[txt_tag[j][1:-1]]
            if p and p[-1] == '\n':
                txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + '\r\n'
            else:
                txt_styled = txt_styled + style[0] + p + style[1]
        return txt_styled

    def _make_mdx_index(self, db_name):
        mdx = MDX(self._mdx_file)
        self._mdx_db = db_name
        index_list = (mdx.get_index())['index_dict_list']
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE MDX_INDEX
               (key_text text,
                file_pos integer,
                compressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )'''
        )

        tuple_list = []
        for item in index_list:
            tuple = (item['key_text'],
                     item['file_pos'],
                     item['compressed_size'],
                     item['record_block_type'],
                     item['record_start'],
                     item['record_end'],
                     item['offset']
                     )
            tuple_list.append(tuple)
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?)',
                      tuple_list)
        # build the metadata table
        meta = (mdx.get_index())['meta']
        c.execute(
            '''CREATE TABLE META
               (key text,
                value text
                )''')

        #for k,v in meta:
        #    c.execute(
        #    'INSERT INTO META VALUES (?,?)', 
        #    (k, v)
        #    )
        
        c.executemany(
            'INSERT INTO META VALUES (?,?)', 
            [('encoding', meta['encoding']),
             ('stylesheet', meta['stylesheet']),
             ('title', meta['title']),
             ('description', meta['description'])
             ]
            )
        
        conn.commit()
        conn.close()
        #set class member
        self._encoding = meta['encoding']
        self._stylesheet = json.loads(meta['stylesheet'])
        self._title = meta['title']
        self._description = meta['description']


    def _make_mdd_index(self, db_name):
        mdd = MDD(self._mdd_file)
        self._mdd_db = db_name
        index_list = mdd.get_index()
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE MDX_INDEX
               (key_text text,
                file_pos integer,
                compressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )'''
        )

        tuple_list = []
        for item in index_list:
            tuple = (item['key_text'],
                     item['file_pos'],
                     item['compressed_size'],
                     item['record_block_type'],
                     item['record_start'],
                     item['record_end'],
                     item['offset']
                     )
            tuple_list.append(tuple)
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?)',
                      tuple_list)
        conn.commit()
        conn.close()

    def get_mdx_by_index(self, fmdx, index):
        fmdx.seek(index['file_pos'])
        record_block_compressed = fmdx.read(index['compressed_size'])
        record_block_type = record_block_compressed[:4]
        record_block_type = index['record_block_type']
        #adler32 = unpack('>I', record_block_compressed[4:8])[0]
        if record_block_type == 0:
            _record_block = record_block_compressed[8:]
            # lzo compression
        elif record_block_type == 1:
            if lzo is None:
                print("LZO compression is not supported")
                # decompress
            header = b'\xf0' + pack('>I', index['decompressed_size'])
            _record_block = lzo.decompress(header + record_block_compressed[8:])
                # zlib compression
        elif record_block_type == 2:
            # decompress
            _record_block = zlib.decompress(record_block_compressed[8:])
        record = _record_block[index['record_start'] - index['offset']:index['record_end'] - index['offset']]
        record = record = record.decode(self._encoding, errors='ignore').strip(u'\x00').encode('utf-8')
        if self._stylesheet:
            record = self._replace_stylesheet(record)
        record = record.decode('utf-8')
        return record

    def get_mdd_by_index(self, fmdx, index):
        fmdx.seek(index['file_pos'])
        record_block_compressed = fmdx.read(index['compressed_size'])
        record_block_type = record_block_compressed[:4]
        record_block_type = index['record_block_type']
        #adler32 = unpack('>I', record_block_compressed[4:8])[0]
        if record_block_type == 0:
            _record_block = record_block_compressed[8:]
            # lzo compression
        elif record_block_type == 1:
            if lzo is None:
                print("LZO compression is not supported")
                # decompress
            header = b'\xf0' + pack('>I', index['decompressed_size'])
            _record_block = lzo.decompress(header + record_block_compressed[8:])
                # zlib compression
        elif record_block_type == 2:
            # decompress
            _record_block = zlib.decompress(record_block_compressed[8:])
        data = _record_block[index['record_start'] - index['offset']:index['record_end'] - index['offset']]        
        return data

    def mdx_lookup(self, keyword):
        conn = sqlite3.connect(self._mdx_db)
        cursor = conn.execute("SELECT * FROM MDX_INDEX WHERE key_text = " + "\"" + keyword + "\"")
        lookup_result_list = []
        mdx_file = open(self._mdx_file,'rb')
        for result in cursor:
            index = {}
            index['file_pos'] = result[1]
            index['compressed_size'] = result[2]
            index['record_block_type'] = result[3]
            index['record_start'] = result[4]
            index['record_end'] = result[5]
            index['offset'] = result[6]
            lookup_result_list.append(self.get_mdx_by_index(mdx_file, index))
        conn.close()
        return lookup_result_list
	
    def mdd_lookup(self, keyword):
        conn = sqlite3.connect(self._mdd_db)
        cursor = conn.execute("SELECT * FROM MDX_INDEX WHERE key_text = " + "\"" + keyword + "\"")
        lookup_result_list = []
        mdd_file = open(self._mdd_file,'rb')
        for result in cursor:
            index = {}
            index['file_pos'] = result[1]
            index['compressed_size'] = result[2]
            index['record_block_type'] = result[3]
            index['record_start'] = result[4]
            index['record_end'] = result[5]
            index['offset'] = result[6]
            lookup_result_list.append(self.get_mdd_by_index(mdd_file, index))
        conn.close()
        return lookup_result_list

    def get_mdd_keys(self, query = ''):
        if not self._mdd_db:
            return []
        conn = sqlite3.connect(self._mdd_db)
        if query:
            if '*' in query:
                query = query.replace('*','%')
            else:
                query = query + '%'
            cursor = conn.execute('SELECT key_text FROM MDX_INDEX WHERE key_text LIKE \"' + query + '\"')
            keys = [item[0] for item in cursor]
        else:
            cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
            keys = [item[0] for item in cursor]
        conn.close()
        return keys

    def get_mdx_keys(self, query = ''):
        conn = sqlite3.connect(self._mdx_db)
        if query:
            if '*' in query:
                query = query.replace('*','%')
            else:
                query = query + '%'
            cursor = conn.execute('SELECT key_text FROM MDX_INDEX WHERE key_text LIKE \"' + query + '\"')
            keys = [item[0] for item in cursor]
        else:
            cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
            keys = [item[0] for item in cursor]
        conn.close()
        return keys



# mdx_builder = IndexBuilder("oald.mdx")
# text = mdx_builder.mdx_lookup('dedication')
# keys = mdx_builder.get_mdx_keys()
# keys1 = mdx_builder.get_mdx_keys('abstrac')
# keys2 = mdx_builder.get_mdx_keys('*tion')
# for key in keys2:
    # text = mdx_builder.mdx_lookup(key)[0]
# pass
