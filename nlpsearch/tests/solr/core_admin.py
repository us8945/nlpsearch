'''
Created on Nov 6, 2017

@author: Uri Smashnov
'''
import unittest
from nlpsearch.lib.solr import Solr

class Test(unittest.TestCase):
    def __init__(self):
        super(Test, self).__init__()
        self.solr = Solr(solr='/apps/solr/solr-7.1.0/bin/solr')
        self.solr.start()
        
    def create_and_delete_core(self):
        returencode, stdout, stderr = self.solr.create_core('test_schema1')
        self.assertEqual(returencode, 0, msg="received: returncode: {}, stdout: {}, stderr{}".format(returencode, stdout, stderr))

        returencode, stdout, stderr = self.solr.delete_core('test_schema1')
        self.assertEqual(returencode, 0, msg="received: returncode: {}, stdout: {}, stderr{}".format(returencode, stdout, stderr))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()