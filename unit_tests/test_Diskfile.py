#!/usr/bin/env python
from __future__ import print_function


import datetime
import os
import shutil
import stat
import unittest

from dbprocessing import DButils
from dbprocessing import Diskfile
from dbprocessing.Diskfile import FilenameError
from dbprocessing.Diskfile import InputError
from dbprocessing import Version


class TestSetup(unittest.TestCase):
    """
    master class for the setup and teardown
    """
    def setUp(self):
        super(TestSetup, self).setUp()
        sqpath = os.path.join(os.path.dirname(__file__), 'RBSP_MAGEIS.sqlite')
        self.sqlworking = sqpath.replace('RBSP_MAGEIS.sqlite', 'working.sqlite')
        shutil.copy(sqpath, self.sqlworking)
        os.chmod(self.sqlworking, stat.S_IRUSR|stat.S_IWUSR)
        self.dbu = DButils.DButils(self.sqlworking)

    def tearDown(self):
        super(TestSetup, self).tearDown()
        self.dbu.closeDB()
        del self.dbu
        os.remove(self.sqlworking)


class DiskfileStaticTests(unittest.TestCase):
    """Tests for the static methods in Diskfile"""
    def test_calcDigest(self):
        """ calcDigest  should behave correctly"""
        self.assertRaises(Diskfile.DigestError, Diskfile.calcDigest, 'idontexist.file')
        with open('IamAfileThatExists.file', 'wb') as f:
            f.write('I am some text in a file')
        real_ans = 'aa42c02f50c92203be933747670bdd512848385e'
        ans = Diskfile.calcDigest('IamAfileThatExists.file')
        self.assertEqual(real_ans, ans)
        with open('IamAfileThatExists.file', 'wb+') as f:
            f.write('I m more text')
        ans = Diskfile.calcDigest('IamAfileThatExists.file')
        self.assertNotEqual (real_ans, ans)
        f.close()
        os.remove('IamAfileThatExists.file')


class DiskfileTests(TestSetup):
    """Tests for Diskfile class"""
    def test_read_error(self):
        """given a file input that is not readable raise ReadError:"""
        self.assertRaises(Diskfile.ReadError, Diskfile.Diskfile, 'wrong input', self.dbu)

    def test_write_error(self):
        """given a file input that is not writeable WriteError"""
        try:
            with open('IamAfileThatExists.file', 'wb') as f:
                f.write('I am some text in a file')
            os.chmod('IamAfileThatExists.file', stat.S_IRUSR)
            self.assertRaises(Diskfile.WriteError, Diskfile.Diskfile, 'IamAfileThatExists.file', self.dbu)

            os.chmod('IamAfileThatExists.file', stat.S_IWUSR|stat.S_IRUSR)
        finally:
            os.remove('IamAfileThatExists.file')
            
    def test_init(self):
        """init does some checking"""
        with open('IamAfileThatExists.file', 'wb') as f:
            f.write('I am some text in a file')
        try:
            a = Diskfile.Diskfile('IamAfileThatExists.file', self.dbu)
        finally:
            os.remove('IamAfileThatExists.file')

    def test_repr(self):
        """Test repr"""
        # File must exist...
        reprfile = 'reprtest.txt'
        with open(reprfile, 'wb') as f:
            f.write('I am some text in a file')

        df = Diskfile.Diskfile(reprfile, self.dbu)

        self.assertTrue(repr(df) == '<Diskfile.Diskfile object: ' + reprfile + '>')
        os.remove(reprfile)

    def raiseUnusedException(self, exceptionName):
        """For testing exceptions not currently used in code"""
        raise exceptionName

    def test_exceptions(self):
        """Test exceptions not raised in code"""
        self.assertRaises(FilenameError, self.raiseUnusedException, FilenameError)
        self.assertRaises(InputError, self.raiseUnusedException, InputError)        

if __name__ == "__main__":
    unittest.main()
