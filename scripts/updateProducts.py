#!/usr/bin/env python2.6


#==============================================================================
# INPUTS
#==============================================================================
# mission name
# satellite name
# product name
## prod name
## product rel path
## prod filename format
## prod level
# <- add the prod
# <- create the inst_prod link
from __future__ import print_function

import ConfigParser
import datetime
import sys

from dbprocessing import DButils
from dbprocessing.Utils import toBool, toNone

sections = ['base', 'product', 'inspector', "code"]
inspector_dict = { 'inspector_output_interface': 'output_interface_version',
                   'inspector_arguments': 'arguments',
                   'inspector_description': 'description',
                   'inspector_newest_version': 'newest_version',
                   'inspector_relative_path': 'relative_path',
                   'inspector_date_written': 'date_written',
                   'inspector_filename': 'filename',
                   'inspector_active': 'active_code' }
code_dict = { 'code_filename': 'filename',
              'code_arguments': 'arguments',
              'code_relative_path': 'relative_path',
              'code_output_interface': 'output_interface_version',
              'code_newest_version': 'newest_version',
              'code_date_written': 'date_written',
              'code_active': 'active_code',
              'code_ram': 'ram',
              'code_cpu': 'cpu' }


def readconfig(config_filepath):
    """
    read in a config file and return a dictionary with the sections as keys and
    the options and values as dictionaries
    """
    # Create a ConfigParser object, to read the config file
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(config_filepath)
    ## lest not use this since it is undocumented magic and might change with versions
    # return cfg._sections # this is an ordered dict of the contents of the conf file
    ans = {}
    for section in cfg.sections():
        ans[section] = {}
        for val in cfg.items(section):
            try:
                ans[section][val[0]] = float(val[1])
            except ValueError:
                ans[section][val[0]] = val[1]
            if ans[section][val[0]] == 'None':
                ans[section][val[0]] = None
            if ans[section][val[0]] == 'True':
                ans[section][val[0]] = True
            if ans[section][val[0]] == 'False':
                ans[section][val[0]] = False
            try:
                ans[section][val[0]] = datetime.datetime.strptime(ans[section][val[0]], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
    return ans

def _updateSections(conf):
    """
    go through each section and update the db is there is a change
    """
    dbu = DButils.DButils('sndd','sage') # TODO don't assume RBSP later
    dbu.openDB()
    dbu._createTableObjects()

    sections = ['mission', 'satellite', 'instrument', 'product',
                'instrumentproductlink', 'inspector', 'process',
                'code']
    succ = 0
    for section in sections:
        # get the object for the section
        try:
            objs = dbu.session.query(dbu.__getattribute__(section.title())).all()
            succ += 1
        except KeyError: 
            continue
        # get the attributes
        print(section)
        for obj in objs:
            same = []
            attrs = [v for v in dir(obj) if v[0] != '_' and v[-2:] != 'id']
            # check if everything is the same or not
            key = section
            dict_keys=attrs
            # select product_name
            if obj.__str__().find("Product") != -1:
                key = "product_" + obj.product_name

            # Handle inspector columns name
            if obj.__str__().find("Inspector") != -1:
                key = "product_" + dbu.session.query(dbu.Product).get(obj.product).product_name
                same = [conf[key][k] == obj.__getattribute__(inspector_dict[k]) for k in inspector_dict.keys()]
                attrs = inspector_dict.values()
                dict_keys = inspector_dict.keys()

            # Handle Process columns name and set product_id
            if obj.__str__().find("Process") != -1:
                key = "process_" + dbu.session.query(dbu.Process).get(obj.process_id).process_name
                product_name = "_".join(conf[key]['output_product'].split('_')[1:])
                product_id = [a.product_id for a in dbu.session.query(dbu.Product).all() 
                              if a.product_name == product_name]
                conf[key]["output_product"] = product_id[0]
                same = [conf[key][v1] == obj.__getattribute__(v1) for v1 in attrs]

            # Handle Code columns name for process
            if obj.__str__().find("Code") != -1:
                key = "process_" + dbu.session.query(dbu.Process).get(obj.process_id).process_name
                same = [conf[key][k] == obj.__getattribute__(code_dict[k]) for k in code_dict.keys()]
                attrs = code_dict.values()
                dict_keys = code_dict.keys()

            if len(same) == 0:
                same = [conf[key][v1] == obj.__getattribute__(v1) for v1 in attrs]
            # print out what is different  DB --- file
            if sum(same) != len(same): # means they are different
                for i, v1 in enumerate(same):
                    if not v1:
                        print('{0}[{1}]  {2} ==> {3}'.format(section, attrs[i], obj.__getattribute__(attrs[i]), conf[key][dict_keys[i]]))
                        obj.__setattr__(attrs[i], conf[key][dict_keys[i]])
                        dbu.session.add(obj)
                dbu.commitDB()
    if succ == 0:
        raise(ValueError('using {0} on a product that is not in the DB'.format(sys.argv[0])))


def usage():
    """
    print the usage message out
    """
    print("Usage: {0} <filename>".format(sys.argv[0]))
    print("   -> config file to update")
    return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
        sys.exit(2)
    conf = readconfig(sys.argv[-1])
    _updateSections(conf)
