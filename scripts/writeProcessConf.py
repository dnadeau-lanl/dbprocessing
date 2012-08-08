#!/usr/bin/env python2.6


# following the recipe in the document I wrote


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

import ConfigParser
import sys

from dbprocessing import DBUtils2


def toBool(value):
    if value in ['True', 'true', True, 1, 'Yes', 'yes']:
        return True
    else:
        return False

def toNone(value):
    if value == '':
        return None
    else:
        return value

def writeconfig(my_cfg, config_filepath):
    cfg=ConfigParser.ConfigParser()
    for section in my_cfg:
        cfg.add_section(section)
        for key in my_cfg[section]:
            cfg.set(section, key, my_cfg[section][key])
    fp=open(config_filepath, "wb")
    cfg.write(fp)
    fp.close()
    print('wrote: {0}'.format(config_filepath))
    return


def getStuff(proc_name, filename):
    cfg = {}
    dbu = DBUtils2.DBUtils2('rbsp') # TODO don't assume RBSP later
    dbu._openDB()
    dbu._createTableObjects()
    # are we trying to write files for all the products?
#    if prod_name.lower() == 'all':
#        prods = dbu.getAllProducts()
#        for prod in prods:
#            getStuff(prod.product_name, prod.product_name + filename)
#        return
    proc_id = dbu.getProcessID(proc_name)
    # get instances of all the tables in a product traceback
    sq = dbu.getProcessTraceback(proc_id)
    for section in sq:
        attrs = dir(sq[section])
        if section in ['input_product', 'productprocesslink']: # special case this is a list
            for ii, sec in enumerate(sq[section]):
                cfg[section + str(ii)] = {}
                attrs = dir(sec[0]) # [0] is the object, [1] is boolean for optional
                for val in attrs:
                    if val[0] != '_':
                        cfg[section + str(ii)][val] = sec[0].__getattribute__(val)
            continue
        cfg[section] = {}
        for val in attrs:
            if val[0] != '_':
                cfg[section][val] = sq[section].__getattribute__(val)
    writeconfig(cfg, filename)


def usage():
    """
    print the usage messag out
    """
    print "Usage: {0} <process name> <filename>".format(sys.argv[0])
    print "   -> process name (or number) to write to config file"
    return


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        sys.exit(2)
    getStuff(sys.argv[1], sys.argv[2])
