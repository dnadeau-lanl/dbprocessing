#!/bin/env python
# This script is to reform level_0 and generate level_1 hdf5.
# Take out primary_header, secondary_header, spacewire_preamble from group senserXXXXXX and creats their own groups.
# Remove 'senserXXXXXX:' from dataset name.
# where XXXXXX is packet type: [EMPSOH, RPPSOH, RFSHigh, RFSLow]

import h5py
import sys
import os
import os.path
import shutil
import logging
import datetime
import glob
import copy
import logging
import logging.handlers
from collections import defaultdict
from optparse import OptionParser
import argparse
import pdb


try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def main():
     
    paths, start, end, force, files = parse()
    #print paths, start, end
    
#    level0_pattern = os.path.join(paths['input'], "*h5")
    file = files[0].split(" ")[0]
    level0_files = glob.glob(os.path.dirname(file)+"/*level_0*h5")
    # all senser-rfs h5 files:emp_soh, rpp_soh, lowband, higband

    for each_level0 in level0_files:                           # each_level0 is full path of level0 file
        level0_fn = os.path.basename(each_level0)              # get level0 filename 
        level1_fn = level0_fn.replace('level_0', 'level_1')
        level1_fn = os.path.join(paths['output'], level1_fn)
        if os.path.isfile(level1_fn):
              print  level1_fn , "exists already, skip it"
              continue
        
        if os.path.isfile(level1_fn) and not force:
             logging.info('Level1 h5 file already exists: ' '{0}'.format(level1_fn))
             continue

        name_list = level0_fn.strip().split('.')
        date_string = '{0}'.format(name_list[1])
        date_time = datetime.datetime.strptime(date_string, '%Y%m%d')
        if date_time < start or  date_time > end:
             continue


        if level1_fn.find('emp_soh') !=-1 :
                packet_type = 'senserEMPSOH'

        elif level1_fn.find('highband') !=-1 :
                packet_type = 'senserRFSHigh'

        elif level1_fn.find('lowband') !=-1 :
                packet_type = 'senserRFSLow'

        elif level1_fn.find('rpp_soh') !=-1 :
                packet_type = 'senserRPPSOH'
        else:
                continue

        shutil.copy(each_level0, level1_fn)
        logging.info('Processing:' '{0}'.format(level0_fn))

        reformat_level0(level1_fn, packet_type)
         
        
def parse():
   """
   Parse the command line arguments and perform error checking
 
   Parameters
   ==========
 
   Returns
   =======
   paths : dictionary
       Input and output filepaths used for processing
   start : datetime.datetime
       Start date/time of processing
   end : datetime.datetime
       End date/time of processing
   options.force : boolean
       Allows overwriting output files

   Examples
   ========
   """
   global options


# Define usage and add options

   # Define default start and end dates
   now = datetime.datetime.utcnow().date()
   date_default = now.strftime("%Y%m%d")

   script_path = os.path.dirname(os.path.abspath(__file__))

   parser = argparse.ArgumentParser( description='Process SENSER L0 Ubet files to L1.')
   parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                      default=False, help='Increases verbosity of logging')

   parser.add_argument('-f', '--force', action='store_true', dest='force',
                      default=False, help='Allow overwriting output files')

   parser.add_argument('-s', '--start', dest='start', default=date_default,
                      help='Start date for processing (format = YYYYMMDD). '
                      'Not used for realtime processing.', metavar='START')

   parser.add_argument('-e', '--end', dest='end', default=date_default,
                      help='End date for processing (format = YYYYMMDD). '
                      'Not used for realtime processing.', metavar='END')
         
   parser.add_argument('-o', '--outpath', dest='outpath',
                      default=None, help='Output path for level 1 HDF5 files',
                      metavar='INPUT_PATH')

   parser.add_argument('-l', '--log_filepath', dest='log_filepath',
                      default=None, help='Log filepath',
                      metavar='LOG_FILEPATH')
   parser.add_argument('files', nargs='*' , help='file name to process')
       

   options = parser.parse_args()
  
   # Setup logging
   setup_logger(options.log_filepath, options.verbose)

   logging.info('Parsing inputs')

   # Check for valid option values
   start, end = option_error_checking(options)

   # Check and define paths
   paths = check_paths(options.outpath)

   # List options
   logging.info('Using the following options:')
   logging.info('--verbose = {0}'.format(options.verbose))
   logging.info('--force = {0}'.format(options.force))
   logging.info('--start = {0}'.format(options.start))
   logging.info('--end = {0}'.format(options.end))
   logging.info('Output path = {0}'.format(paths['output']))
   logging.info('Log filepath = {0}'.format(options.log_filepath))

   return paths, start, end, options.force, options.files


def setup_logger(log_filepath, verbose):
    """
    Setup logging to file and to stdout/stderr

    Parameters
    ==========
    log_filepath : string
        Filepath for the logging file
    verbose : boolean
        Verbosity of output

    Returns
    =======

    Examples
    ========
    """
    # Check that logging file is defined
    err_msg = 'Logging file is undefined: {0}'.format(log_filepath)
    assert(log_filepath is not None), err_msg

    # Define log formatting and logging level
    log_formatter = logging.Formatter('%(asctime)s - %(message)s')
    logger = logging.getLogger()

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # File handler (controls logging to file)
    file_handler = logging.handlers.RotatingFileHandler(log_filepath,
                                                        maxBytes=1e7,
                                                        backupCount=10)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Stream handler (controls logging to stdout/stderr)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)


def option_error_checking(options):
    '''
    Check the options object for valid values

    Parameters
    ==========
    options : OptionParser object
        Contains all command line options

    Returns
    =======
    start : datetime.datetime
        Starting date/time
    end : datetime.datetime
        Ending date/time
    '''
    # Check for acceptable start and end dates
    try:
        start = datetime.datetime.strptime(options.start, '%Y%m%d')
    except:
        err_msg = ('Could not convert start date ({0}) to datetime. '
                   'Use --start STARTDATE (e.g. --start 20100101) to '
                   'specify start date').format(options.start)
        logging.exception(err_msg)
        raise Exception(err_msg)

    try:
        end = datetime.datetime.strptime(options.end, '%Y%m%d')
    except:
        err_msg = ('Could not convert end date ({0}) to datetime. '
                   'Use --end ENDDATE (e.g. --end 20100101) to '
                   'specify end date').format(options.start)
        logging.exception(err_msg)
        raise Exception(err_msg)

    return start, end



def check_paths(outpath):
    """
    Perform error checking in input and output path

    Parameters
    ==========
    outpath : string
        Path for Level 1 output files

    Returns
    =======
    paths : dictionary
        All paths used in processing

    Examples
    ========
    """
    # Create filepaths dictionary
    paths = {}
    paths['output'] = outpath

    # Loop over input and output paths
    for key in paths.keys():

        name = key.capitalize()

        # Check for defined paths
        err_msg = '{0} path is undefined: {1}'.format(name, paths[key])
        assert(paths[key] is not None), err_msg

        # Check that directory or file exists
        err_msg = '{0} directory does not exist: {1}'.format(name, paths[key])
        assert(os.path.exists(paths[key])), err_msg

    return paths



def reformat_level0(level1_fn, packet_type):

    l0 = h5py.File(level1_fn, 'r+')

    for each_grp in l0.keys():
        if each_grp == 'metadata':
             continue
        else:
             l0_var_lst = l0[each_grp].keys()

             for each_var in l0_var_lst:

                  l0_path = '/'+ packet_type + '/' + each_var
         
                  if l0_path.find('primary_header') !=-1:
                         old_l0 = '/' + str(packet_type) + '/primary_header:'
                         new_l1 = l0_path.replace(old_l0, '')
                         new_l1 = 'packet_data/primary_header/' + new_l1
                         l0[new_l1] = l0[l0_path]
                         del l0[l0_path]
                         continue

                  if l0_path.find('secondary_header') !=-1:
                         old_l0 = '/' + str(packet_type) + '/secondary_header:'
                         new_l1 = l0_path.replace(old_l0, '')
                         new_l1= '/packet_data/secondary_header/' + new_l1
                         l0[new_l1] = l0[l0_path]
                         del l0[l0_path]
                         continue

                  if l0_path.find('spacewire_preamble') !=-1:
                         old_l0 = '/' + str(packet_type) + '/spacewire_preamble:'
                         new_l1 = l0_path.replace(old_l0, '')
                         new_l1 = '/packet_data/spacewire_preamble/' + new_l1
                         l0[new_l1] = l0[l0_path]
                         del l0[l0_path]
                         continue
                  
                  filter_var = packet_type + ":"
                  new_tmp = l0_path.replace(filter_var, "")
                  new_l1 = new_tmp.replace(packet_type, "app_data")
  
                  if new_l1.find('mask') != -1:      
                       del l0[l0_path]
                       continue
                  
                  if new_l1.find('was_truncated') != -1:      
                       new_l1 = 'app_data/was_truncated'
                       l0[new_l1] = l0[l0_path]
                       del l0[l0_path]
                       continue

                  if new_l1.find('packet_crc') != -1:      
                       new_l1 = 'packet_data/packet_crc'
                       l0[new_l1] = l0[l0_path]
                       del l0[l0_path]
                       continue
                       
                  # remove all field names before : for array
                  if new_l1.find(":") == -1:     # no nested structures or array
                      l0[new_l1] = l0[l0_path]
                      del l0[l0_path]
                      continue
                  
                  fields = new_l1.split(":")
                  var_name = fields[-1]
                  packet_name = fields[0].split("/")[1]
                  new_l1 = packet_name +"/" +  var_name
                  l0[new_l1] = l0[l0_path]
                  del l0[l0_path]
                   
    
    del l0[packet_type]        #delete empty group
    l0.close()



if __name__ == "__main__":

    main()

