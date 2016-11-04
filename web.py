from flask import Flask, send_from_directory
from mdict_dir import Dir
from mdict_query import IndexBuilder
import os

IndexBuilder('vocab.mdx')
pass

app = Flask(__name__)
# add reg support
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
                super(RegexConverter, self).__init__(url_map)
                self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter
#################

# init mdx

mdict = Dir('mdx')
config = mdict._config['dicts'][1]
builder = config['builder']

##########

@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/dicts')
def all_dicts():
    responce = ''
    for dd in mdict._config['dicts']:
        responce = responce + dd['dict_name'] + '\n'
    return responce

@app.route('/search/<regex(".+?\."):base><regex("css|png|jpg|gif|mp3|js"):ext>')
def getFile(base,ext):

    if os.path.isfile('mdx\\{0}{1}'.format(base,ext)):
        return send_from_directory('mdx','{0}{1}'.format(base,ext))

    if not os.path.isfile('static\\{0}{1}'.format(base, ext).replace('/','_')):
        #return 'haha'
        cssname = builder.get_mdd_keys('*{0}{1}'.format(base,ext).replace("/","\\"))[0]
        cssbyte = builder.mdd_lookup(cssname)[0]
        cssfile = open('static\\{0}{1}'.format(base, ext).replace('/','_'),'wb')
        cssfile.write(cssbyte)
        cssfile.close()
    return send_from_directory('static','{0}{1}'.format(base, ext).replace('/','_'))


@app.route('/search/<hwd>')
def search(hwd):
    text = builder.mdx_lookup(hwd)[0]
    return text.replace("\r\n","").replace("entry://","").replace("sound://","")
    
if __name__ == '__main__':
   app.run('127.0.0.1',5000, debug = True)
   