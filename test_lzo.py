from mdict_query import IndexBuilder

bd = IndexBuilder("mdx\\lls.mdx")
keys = bd.get_mdx_keys("ded*")
result = bd.mdx_lookup('a')
pass