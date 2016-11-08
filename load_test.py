from mdict_query import IndexBuilder
import webbrowser
ib = IndexBuilder("mdx/LDOCE6.mdx")
key = ib.get_mdx_keys("b*")[1:10]
for i in key:
	webbrowser.open("http://128.199.107.96:5000/dict/ldoce615095/{0}".format(i))