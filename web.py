from flask import Flask, send_from_directory
from mdict_dir import Dir
#from mdict_query import IndexBuilder
import os
import re
#IndexBuilder('vocab.mdx')
#pass

app = Flask(__name__)
# add reg support
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
                super(RegexConverter, self).__init__(url_map)
                self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter
#################

# 将词典名转为用于url的形式
def title2url(title):
    return re.sub(r"。|，|？|\s|,|\.|/|\\|", "", title.lower())
# init mdx

mdict = Dir('mdx')
config = mdict._config['dicts'][0]
mdx_map = {}
for dic in mdict._config['dicts']:
    mdx_map[title2url(dic['title'])] = dic['builder']
##########

@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/dict/')
def all_dicts():
    responce = ''
    for key in mdx_map:
        responce = responce + "<p><a>{0}</a></p>".format(key)
    return responce

@app.route('/dict/<title>/<regex(".+?\."):base><regex("css|png|jpg|gif|mp3|js"):ext>')
def getFile(title,base,ext):
    if title not in mdx_map:
        return "没有找到此词典"
    builder = mdx_map[title]
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


@app.route('/dict/<title>/<hwd>')
def search(title, hwd):
    if title not in mdx_map:
        return "没有找到此词典"
    builder = mdx_map[title]
    result = builder.mdx_lookup(hwd)
    if result:
        text = result[0]
    else:
        return "<p>在词典{0}中没有找到{1}</p>".format(title, hwd)

    return text.replace("\r\n","").replace("entry://","").replace("sound://","")
    
if __name__ == '__main__':
   app.run('127.0.0.1',5000, debug = True)
   