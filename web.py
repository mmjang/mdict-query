from flask import Flask, send_from_directory, abort, render_template, jsonify, Response
from mdict_dir import Dir
#from mdict_query import IndexBuilder
import os
import re
import sys
import json
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
# 将多层路径整合为文件名
def path2file(path):
    return path.replace('/','_')
# 将词典名转为用于url的形式
def title2url(title):
    return re.sub(r"。|，|？|\s|,|\.|/|\\|(|)|（|）", "", title.lower())
# init app
mdict_dir = 'mdx' # mdx/mdd 文件目录
mdd_cache_dir = 'cache'

if not os.path.isdir(mdict_dir):
    print('no mdx directory\n', file=sys.stderr)
    os.makedirs(mdict_dir)

if not os.path.isdir(mdd_cache_dir):
    os.makedirs(mdd_cache_dir)


mdict = Dir(mdict_dir)
#config = mdict._config['dicts'][0]
mdx_map = {}
for dic in mdict._config['dicts']:
    mdx_map[title2url(dic['title'])] = dic['builder']
##########
@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/dict/')
def all_dicts():
    dicts = []
    for dic in mdict._config['dicts']:
        title = dic['title']
        dicts.append({
                'title' : title,
                'url' : '/dict/{0}/'.format(title2url(title))
                })
    return render_template('all.html', dicts = dicts)

@app.route('/dict/<title>/')
def description(title):
    if title not in mdx_map:
        return "没有找到此词典"
    for xxx in mdict._config['dicts']:
        if title2url(xxx['title']) == title:
            return render_template("dict.html", title = xxx['title'], description = xxx['description'], url_title = title)
  

@app.route('/dict/search/<query>/')
def search(query):
    result = []
    for xxx in mdict._config['dicts']:
       bd = xxx['builder']
       result.append([title2url(xxx['title']), bd.get_mdx_keys(query)])
    dat = json.dumps(result, ensure_ascii = False)
    resp = Response(response=dat, # standard way to return json
            status=200, 
            mimetype="application/json")
    return(resp)


@app.route('/dict/<title>/<regex(".+?\."):base><regex("css|png|jpg|gif|mp3|js|wav|ogg"):ext>')
def getFile(title,base,ext):
    #print(base + ext, file=sys.stderr)
    if title not in mdx_map:
        return "没有找到此词典"
    builder = mdx_map[title]
    # 是否为外挂文件
    external_file = os.path.join(mdict_dir, base + ext)
    if os.path.isfile(external_file):
        return send_from_directory(mdict_dir, base + ext)
    
    # 是否是mdd内的文件
    cache_name = path2file(base + ext)
    cache_full = os.path.join(mdd_cache_dir, cache_name)
    if not os.path.isfile(cache_full):
        mdd_key = '\\{0}{1}'.format(base,ext).replace("/","\\")
        byte = builder.mdd_lookup(mdd_key)
        if not byte: # 在 mdd 内未找到指定文件
            abort(404) # 返回 404
        file = open(cache_full,'wb')
        file.write(byte[0])
        file.close()
    return send_from_directory(mdd_cache_dir, cache_name)


@app.route('/dict/<title>/<hwd>')
def getEntry(title, hwd):
    if title not in mdx_map:
        return "没有找到此词典"
    builder = mdx_map[title]
    result = builder.mdx_lookup(hwd)
    if result:
        text = result[0]
    else:
        return "<p>在词典{0}中没有找到{1}</p>".format(title, hwd)

    #return
    #text.replace("\r\n","").replace("entry://","").replace("sound://","")
    return render_template("entry.html", content = text, title = title, entry = hwd)
    
if __name__ == '__main__':
   app.run('127.0.0.1',5000, debug = True)
   
