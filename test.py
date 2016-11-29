from mdict_query import IndexBuilder
import unittest
import os
import glob
import time
from timeit import timeit

class TestMdict(unittest.TestCase):

    _mdx_file = glob.glob("mdx/Vocabulary*.mdx")[0]
    _repeat = 100
    # remove existing db
    for f in glob.glob("mdx/Vocabulary*.db"):
        os.remove(f)
     
    def test_builder_noindex(self):
        '''test basic function'''
        for f in glob.glob("mdx/Vocabulary*.db"):
            os.remove(f)
        print("***without sql index***\n")
        start = time.time() 
        bd = IndexBuilder(self._mdx_file, sql_index = False, check = True)
        print("takes {0} seconds to build without sql index\n".format(time.time() - start))         
        
        start = time.time()
        word = 'dedicate'
        for i in range(self._repeat):
            self.assertTrue(bd.mdx_lookup(word))
        print("takes {0} second to lookup {1} {2} times\n".format(time.time() - start, word, self._repeat))
        for i in range(self._repeat):
            bd.get_mdx_keys("dedi*")
        print("takes {0} second to lookup {1} {2} times\n".format(time.time() - start, "dedi*", self._repeat))
         
    def test_builder_index(self):
        '''test basic function'''
        for f in glob.glob("mdx/Vocabulary*.db"):
            os.remove(f)
        print("***with sql index***\n")
        start = time.time() 
        bd = IndexBuilder(self._mdx_file, sql_index = True, check = False)
        print("takes {0} seconds to build with sql index\n".format(time.time() - start))
         
        start = time.time()
        word = 'dedicate'
        for i in range(self._repeat):
            bd.mdx_lookup(word)
        print("takes {0} second to lookup {1} {2} times\n".format(time.time() - start, word, self._repeat))

        for i in range(self._repeat):
            bd.get_mdx_keys("dedi*")
        print("takes {0} second to lookup {1} {2} times\n".format(time.time() - start, "dedi*", self._repeat))
 

if __name__ == '__main__':
        unittest.main()