from mdict_query import IndexBuilder

bd = IndexBuilder("larouss.mdx")
keys = bd.get_mdx_keys("ded*")
result = bd.mdx_lookup(keys[0])
pass