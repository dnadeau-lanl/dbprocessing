#!/usr/bin/env python
from __future__ import print_function

"""Unit tests for runMe module, including runMe class and related"""

__author__ = 'Jonathan Niehof <Jonathan.Niehof@unh.edu>'

import datetime
import os
import os.path
import shutil
import tempfile
import unittest

#The log is opened on import, so need to quarantine the log directory
#right away
os.environ['DBPROCESSING_LOG_DIR'] = os.path.join(os.path.dirname(__file__),
                                                  'unittestlogs')
import dbprocessing.DButils
import dbprocessing.runMe


class RunMeCmdArgTests(unittest.TestCase):
    """Tests command, argument, and command line building"""

    def setUp(self):
        """Make a copy of db and open it so have something to work with"""
        super(RunMeCmdArgTests, self).setUp()
        self.td = tempfile.mkdtemp()
        shutil.copy2(
            os.path.join(os.path.dirname(__file__), 'RBSP_MAGEIS.sqlite'),
            self.td)
        self.dbu = dbprocessing.DButils.DButils(os.path.join(
            self.td, 'RBSP_MAGEIS.sqlite'))

    def tearDown(self):
        """Remove the copy of db"""
        self.dbu.closeDB()
        del self.dbu
        shutil.rmtree(self.td)
        super(RunMeCmdArgTests, self).tearDown()

    def testSimpleArgs(self):
        """Check for simple command line arguments"""
        #Fake the processqueue (None)
        #Use process 38 (mageis L2 combined) and all mandatory
        #inputs for one day
        #Bump version, because output already exists
        rm = dbprocessing.runMe.runMe(
            self.dbu, datetime.date(2013, 9, 21), 38,
            [5774, 5762, 1791, 5764], None, version_bump=2)
        #Make sure this is runnable
        self.assertTrue(rm.ableToRun)
        #Components of the command line
        self.assertEqual(['TEMPLATE-L2.cdf', 'v1.3.4', 'v1.0.8'], rm.args)
        self.assertEqual([], rm.extra_params)
        self.assertEqual(
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            rm.codepath)
        self.assertEqual(
            'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf',
            rm.filename)
        #And now the command line itself
        rm.make_command_line()
        shutil.rmtree(rm.tempdir) #remove the dir made for the command
        self.assertEqual([
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            'TEMPLATE-L2.cdf', 'v1.3.4', 'v1.0.8',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisHIGH-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisLOW-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/MagEphem/predicted/b/'
            'rbspb_pre_MagEphem_OP77Q_20130921_v1.0.0.txt',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisM75-L2_20130921_v3.0.0.cdf',
            os.path.join(rm.tempdir,
                         'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf')
        ], rm.cmdline)

    def testSubRootdir(self):
        """Check for specifying ROOTDIR in arguments"""
        code = self.dbu.getEntry('Code', 38)
        code.arguments = '-m {ROOTDIR}/TEMPLATE-L2.cdf'
        self.dbu.session.add(code)
        self.dbu.commitDB()
        rm = dbprocessing.runMe.runMe(
            self.dbu, datetime.date(2013, 9, 21), 38,
            [5774, 5762, 1791, 5764], None, version_bump=2)
        self.assertTrue(rm.ableToRun)
        #Components of the command line
        self.assertEqual(['-m', '/n/space_data/cda/rbsp/TEMPLATE-L2.cdf'],
                         rm.args)
        self.assertEqual([], rm.extra_params)
        self.assertEqual(
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            rm.codepath)
        self.assertEqual(
            'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf',
            rm.filename)
        rm.make_command_line()
        shutil.rmtree(rm.tempdir) #remove the dir made for the command
        self.assertEqual([
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            '-m', '/n/space_data/cda/rbsp/TEMPLATE-L2.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisHIGH-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisLOW-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/MagEphem/predicted/b/'
            'rbspb_pre_MagEphem_OP77Q_20130921_v1.0.0.txt',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisM75-L2_20130921_v3.0.0.cdf',
            os.path.join(rm.tempdir,
                         'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf')
        ], rm.cmdline)

    def testSubRootdirProcess(self):
        """Check for specifying ROOTDIR in process 'extras'"""
        process = self.dbu.getEntry('Process', 38)
        process.extra_params = '-d|{ROOTDIR}'
        self.dbu.session.add(process)
        self.dbu.commitDB()
        rm = dbprocessing.runMe.runMe(
            self.dbu, datetime.date(2013, 9, 21), 38,
            [5774, 5762, 1791, 5764], None, version_bump=2)
        self.assertTrue(rm.ableToRun)
        #Components of the command line
        self.assertEqual(['TEMPLATE-L2.cdf', 'v1.3.4', 'v1.0.8'], rm.args)
        self.assertEqual(['-d', '/n/space_data/cda/rbsp'], rm.extra_params)
        self.assertEqual(
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            rm.codepath)
        self.assertEqual(
            'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf',
            rm.filename)
        rm.make_command_line()
        shutil.rmtree(rm.tempdir) #remove the dir made for the command
        self.assertEqual([
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            '-d', '/n/space_data/cda/rbsp',
            'TEMPLATE-L2.cdf', 'v1.3.4', 'v1.0.8',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisHIGH-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisLOW-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/MagEphem/predicted/b/'
            'rbspb_pre_MagEphem_OP77Q_20130921_v1.0.0.txt',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisM75-L2_20130921_v3.0.0.cdf',
            os.path.join(rm.tempdir,
                         'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf')
        ], rm.cmdline)

    def testSubCodedir(self):
        """Check for specifying CODEDIR in arguments"""
        code = self.dbu.getEntry('Code', 38)
        code.arguments = '-m {CODEDIR}/TEMPLATE-L2.cdf'
        self.dbu.session.add(code)
        self.dbu.commitDB()
        rm = dbprocessing.runMe.runMe(
            self.dbu, datetime.date(2013, 9, 21), 38,
            [5774, 5762, 1791, 5764], None, version_bump=2)
        self.assertTrue(rm.ableToRun)
        #Components of the command line
        self.assertEqual([
            '-m', '/n/space_data/cda/rbsp/codes/mageis/TEMPLATE-L2.cdf'],
                         rm.args)
        self.assertEqual([], rm.extra_params)
        self.assertEqual(
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            rm.codepath)
        self.assertEqual(
            'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf',
            rm.filename)
        rm.make_command_line()
        shutil.rmtree(rm.tempdir) #remove the dir made for the command
        self.assertEqual([
            '/n/space_data/cda/rbsp/codes/mageis/'
            'run_mageis_L2combined_v3.0.0.py',
            '-m', '/n/space_data/cda/rbsp/codes/mageis/TEMPLATE-L2.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisHIGH-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisLOW-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/MagEphem/predicted/b/'
            'rbspb_pre_MagEphem_OP77Q_20130921_v1.0.0.txt',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisM75-L2_20130921_v3.0.0.cdf',
            os.path.join(rm.tempdir,
                         'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf')
        ], rm.cmdline)

    def testSubCodever(self):
        """Use code version in path and arguments"""
        code = self.dbu.getEntry('Code', 38)
        code.arguments = '-v {CODEVERSION}'
        code.relative_path = 'codes/mageis_{CODEVERSION}/'
        code.filename = 'run_mageis_L2combined_{CODEVERSION}.py'
        self.dbu.session.add(code)
        self.dbu.commitDB()
        rm = dbprocessing.runMe.runMe(
            self.dbu, datetime.date(2013, 9, 21), 38,
            [5774, 5762, 1791, 5764], None, version_bump=2)
        self.assertTrue(rm.ableToRun)
        self.assertEqual(['-v', '3.0.0'], rm.args)
        self.assertEqual([], rm.extra_params)
        self.assertEqual(
            '/n/space_data/cda/rbsp/codes/mageis_3.0.0/'
            'run_mageis_L2combined_3.0.0.py',
            rm.codepath)
        self.assertEqual(
            'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf',
            rm.filename)
        rm.make_command_line()
        shutil.rmtree(rm.tempdir) #remove the dir made for the command
        self.assertEqual([
            '/n/space_data/cda/rbsp/codes/mageis_3.0.0/'
            'run_mageis_L2combined_3.0.0.py',
            '-v', '3.0.0',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisHIGH-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisLOW-L2_20130921_v3.0.0.cdf',
            '/n/space_data/cda/rbsp/MagEphem/predicted/b/'
            'rbspb_pre_MagEphem_OP77Q_20130921_v1.0.0.txt',
            '/n/space_data/cda/rbsp/rbspb/mageis_vc/level2/int/'
            'rbspb_int_ect-mageisM75-L2_20130921_v3.0.0.cdf',
            os.path.join(rm.tempdir,
                         'rbspb_int_ect-mageis-L2_20130921_v3.0.1.cdf')
        ], rm.cmdline)



if __name__ == '__main__':
    unittest.main()

