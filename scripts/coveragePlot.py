#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 10:30:27 2014

@author: balarsen

"""
from __future__ import division

import ConfigParser
import copy
import datetime
import fnmatch
import itertools
import subprocess
from optparse import OptionParser
import os

import dateutil.parser as dup
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
import numpy as np
import spacepy.toolbox as tb

from dbprocessing import Utils
from dbprocessing import DBUtils

echo = False

cmap = LinearSegmentedColormap.from_list('cmap', ['r', 'g', 'y', 'grey'], N=4)

def readconfig(config_filepath):
    # Create a ConfigParser object, to read the config file
    cfg=ConfigParser.SafeConfigParser()
    cfg.read(config_filepath)
    sections = cfg.sections()
    # Read each parameter in turn
    ans = {}
    for section in sections:
        ans[section] = dict(cfg.items(section))
    return ans

def _fileTest(filename):
    """
    open up the file as txt and do a check that there are no repeated section headers
    """
    def rep_list(inval):
        seen = set()
        seen_twice = set( x for x in inval if x in seen or seen.add(x) )
        return list(seen_twice)

    with open(filename, 'r') as fp:
        data = fp.readlines()
    data = [v.strip() for v in data if v[0] == '[']
    seen_twice = rep_list(data)
    if seen_twice:
        raise(ValueError('Specified section(s): "{0}" is repeated!'.format(seen_twice) ))

def _processSubs(conf):
    """
    go through the conf object and deal with any substitutions

    this works by looking for {}
    """
    for key in conf:
        for v in conf[key]:
            while True:
                if isinstance(conf[key][v], (str,unicode)):
                    if '{' in conf[key][v] and '}' in conf[key][v]:
                        sub = conf[key][v].split('{')[1].split('}')[0]
                        if sub == 'TODAY':
                            sub_v = datetime.date.today().strftime('%Y%m%d')
                        elif 'DAYS' in sub:
                            sub_v = "**days=7**"
                        else:
                            raise(NotImplementedError("Unsupported substitution {0} found".format(sub)))
                        conf[key][v] = conf[key][v].replace('{' + sub + '}', sub_v)
                    else:
                        break
                else:
                    break
    return conf

def _processDates(conf):
    """
    update the dates where there can be dates
    """
    keys = ['enddate', 'startdate']
    ans = {}
    for key in keys:
        if isinstance(conf['settings'][key], (datetime.date, datetime.datetime)):
            continue # already a datetime
        ans[key] = None
        try:
            ans[key] = dup.parse(conf['settings'][key])
        except ValueError:
            if '**' in conf['settings'][key]:
                # split an get the date part
                date = dup.parse(conf['settings'][key].split()[0])
                del_date = conf['settings'][key].split('**')[1]
                del_num = del_date.split('=')[1]
                del_date = del_date.split('=')[0]
                if del_date == 'days':
                    ans[key] = date + datetime.timedelta(days=int(del_num))
                else:
                    raise(NotImplementedError("Unsupported substitution {0} found".format(del_date)))

        try:
            conf['settings'][key] = ans[key].date()
        except AttributeError:
            conf['settings'][key] = ans[key]
            
    return conf

def _get_nplots(conf):
    """
    see how many plots are in the panel
    """
    return sum([1 for v in conf['panel'] if v.startswith('plot')])

def _get_nproducts(conf, plotnum):
    """
    given conf and a plot num return the number of products
    """
    return sum([1 for v in conf['plot{0}'.format(plotnum)] if v.startswith('product')
               and 'glob' not in v and 'version' not in v ])

def _get_yticklabels(conf, plotnum):
    """
    given conf and a plot num get the ylabels
    """
    labels = [(v, conf['plot{0}'.format(plotnum)][v]) for v in conf['plot{0}'.format(plotnum)] if v.startswith('yticklabel')]
    return zip(*sorted(labels, key=lambda x: x[0]))[1]
    
def _combine_coverage(inval):
    """
    given the ans nested list make numpy arrays that can be plotted
    """
    out = []
    nplots = len(inval)
    for np_ in range(nplots): # this is the plot
        out.append([])
        for ind_t, t in enumerate(inval[np_]): # this is the date range
            out[np_].append([])
            for nprod in inval[np_][ind_t]: # this is the product
                out[np_][ind_t].append( np.require(zip(*ans[np_][ind_t])[1]))
                # [0][0] is bcease all prods have same dates and we want the first
                out[np_][ind_t].append( ans[np_][ind_t][0][0] ) 
    return out




if __name__ == "__main__":
    usage = "usage: %prog [options] configfile"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    conffile = os.path.expanduser(os.path.expandvars(os.path.abspath(args[0])))
    if not os.path.isfile(conffile):
        parser.error("could not read config file: {0}".format(conffile))
        
    conf = readconfig(conffile)
    conf = _processSubs(conf)
    conf = _processDates(conf)

    # figure out the dates we are going to use
    # make a range of dates
    dates = list(Utils.expandDates(conf['settings']['startdate'], conf['settings']['enddate']))
    dates = [v.date() for v in dates]
    dates = list(Utils.chunker(dates, int(conf['panel']['daysperplot'])))

    # make the arrays that hold the files
    dbu = DBUtils.DBUtils(conf['settings']['mission'], echo=echo)

    # go through the panel and see how many plots there are
    nplots = _get_nplots(conf)

    ans = []

    for pnum, ind_pnum in enumerate(range(nplots), 1):
        ans.append([])
        n_prods = _get_nproducts(conf, pnum)
        prods = []
        for ind_d, d in enumerate(dates):
            ans[ind_pnum].append([])

            for pn, ind_pn in enumerate(range(n_prods), 1):
                ans[ind_pnum][ind_d].append([])
                product_id = dbu.getProductID(conf['plot{0}'.format(pnum)]['product{0}'.format(pn)])
                # print pnum, n_prods, product_id

                ans[ind_pnum][ind_d][ind_pn].append(d)
                ans[ind_pnum][ind_d][ind_pn].append(np.zeros(len(d), dtype=int))
                files = dbu.getFilesByProductDate(product_id, [d[0], d[-1]], newest_version=True)
                #print  len(d), pnum, n_prods, product_id, len(files)
                # cull the files list based on productN_glob
                if 'product{0}_glob'.format(pn) in conf['plot{0}'.format(pnum)]:
                    files_tmp = []
                    for f in files:
                        if fnmatch.fnmatch(f.filename,
                                           conf['plot{0}'.format(pnum)]['product{0}_glob'.format(pn)]):
                            files_tmp.append(f)
                    files = files_tmp
                if 'product{0}_version'.format(pn) in conf['plot{0}'.format(pnum)]:
                    files_tmp = []
                    for f in files:
                        if (dbu.getVersion(f.file_id) >=
                            Utils.parseVersion(conf['plot{0}'.format(pnum)]['product{0}_version'.format(pn)])):
                            files_tmp.append(f)
                    files = files_tmp
                # now that we have all the files loop through and the the dates that we have to 1
                f_dates = [f.utc_file_date for f in files]
                for fd in f_dates:
                    ans[ind_pnum][ind_d][ind_pn][1][ans[ind_pnum][ind_d][ind_pn][0].index(fd)] = 1


    # and make the plots
    out = _combine_coverage(ans)

    outfiles = []
    for ind_d, d in enumerate(out[0]): # loop over the times
        fig = plt.figure(figsize=(20, 8))

        axes = []
        for i in range(nplots):
            axes.append(fig.add_subplot(nplots,1,i+1))

        # set the titles
        axes[0].set_title(conf['panel']['title'], fontsize='larger')
        for i, ax in enumerate(axes, 1):
            ax.set_ylabel(conf['plot{0}'.format(i)]['ylabel'], fontsize='larger')    

            # plot in the color
            ax.imshow(out[i-1][ind_d][0], cmap=cmap, vmin=0, vmax=3,
                      interpolation='nearest', aspect='auto')

            yticklabels = _get_yticklabels(conf, i)

            ax.set_yticks(np.arange(out[0][ind_d][0].shape[0]))
            ax.set_yticklabels(yticklabels)
            ax.set_ylim(tb.bin_center_to_edges(range(out[0][ind_d][0].shape[0]))[0],
                        tb.bin_center_to_edges(range(out[0][ind_d][0].shape[0]))[-1])
            for i in tb.bin_center_to_edges(range(out[0][ind_d][0].shape[0])):
                ax.axhline(i, color='k')

            steps = np.arange(out[0][ind_d][0].shape[1])

            diff = np.diff(steps)[0]/2
            for ii, i in enumerate(steps):
                if ii % 3 == 0:
                    ax.axvline(i+diff, color='k', lw=2)
                else:
                    ax.axvline(i+diff, color='k', lw=1)
            ## ax.set_xlim(xlim)
            ax.set_xticks(steps[::3])#+diff)
            ax.set_xticklabels(out[0][ind_d][1][::3])
            ax.set_xlabel('{0} to {1}'.format(out[0][ind_d][1][0].strftime("%Y-%m-%d"),
                                   out[0][ind_d][1][-1].strftime("%Y-%m-%d")), fontsize='larger')
            fig.autofmt_xdate()

        outfiles.append(conf['settings']['filename_format'] + '_{0}.{1}'
                    .format(ind_d, conf['settings']['outformat']))
        plt.savefig( outfiles[-1] )
        print("Wrote: {0}".format(outfiles[-1]))

    cmd = ['pdftk'] + outfiles + ['cat', 'output']
    cmd += [os.path.expanduser(os.path.expandvars(os.path.abspath(conf['settings']['filename_format']))) + '.{0}'
                    .format(conf['settings']['outformat'])]
    print("Running: {0}".format(' '.join(cmd)))
    subprocess.call(cmd)
    for v in outfiles:
        os.remove(v)

        
