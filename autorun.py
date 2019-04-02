#!/usr/bin/python
# Created by Yi Shen 2019-02-07
import argparse
import directories as dirs
import binaries as bins
import os.path as path
import os
from collections import namedtuple
import subprocess
from MulPtrace import mulptrace
from getCurrent import getCurrent
from getV11 import getV11
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ls', action='store_true', help="Show all simulation names with simulated cores")
    parser.add_argument('name', metavar='Name', type=str, help='Name to characterize this simulation analysis', nargs="?", default=0)
    parser.add_argument('-n', type=str, help='Number of CPU cores to be analysed, only 2-core are strictly simulated while 4,8,16 are duplicated from 2-core')
    args = parser.parse_args()

    # shown previous simulations names for easy naming
    if args.ls:
        show_exps()
        return 0
    if not (args.name and args.n):
        print("-n is mandatory when name is specified")
    configs = get_names(args.name, args.n)
    # cleaning because all files are written in "a" mode.
    subprocess.call([ \
        "rm", "-rf", \
        configs.gridIR, \
        configs.vtrace, \
        configs.powerG, \
        configs.rawpG,  \
        configs.current, \
        configs.vStep, \
        configs.iStep \
        ])
    # check if power trace of 2 core CPU has been translated
    if path.exists(configs.pt):
        if path.exists(configs.pt2c):
            # check if mcpat been run
            if path.exists(configs.op):
                # check if tempaltes are filled
                if path.exists(configs.XML):
                    # check if Gem5 been run
                    if path.exists(configs.M5):
                        #Do gem5
                        pass
                    # Do Gem5 2 mcpat
                #Do mcpat
            # Do mcpat 2 pt
        # Do Multi trace

    # Do voltspot
    baseTime = 0.125 # 0.125 hour for a hypothetical 1-core CPU
    time = str(baseTime * int(args.n) * int(args.n)) + "h"
    FNULL = open(os.devnull, 'w')
    subprocess.call([\
        "timeout", time, \
        bins.voltspot, \
        "-c", configs.pdn, \
        "-f", configs.flp, \
        "-p", configs.pt, \
        "-v", configs.vtrace, \
        "-gridvol_file", configs.gridIR, \
        "-v_step_outfile", configs.vStep, \
        "-i_step_outfile", configs.iStep], \
        stdout=FNULL)
    # get current (legacy)
    subprocess.call(["mv", configs.rawpG, configs.powerG])
    getCurrent(configs.powerG, configs.gridIR, configs.current)
    # get v11
    getV11(configs.gridIR, configs.v11)




def show_exps():
    """show all the names of previous analysis
    """

    for root, dirss, files in os.walk(dirs.dump):
        for name in files:
            if name.endswith((".current")):
                exp = name.split('.')
                print(exp[0])
def get_names(sname, n):
    """Generate the file names of inputs and outputs for all analysis tools
    Capitalized field indicates folder. 

    Arguments:
        name {str} -- name characterising the analysis
        n {str} -- number of cores 
    Returns:
        configs{tuple} -- names
"""
    name = sname + n + 'c'  # example4c
    class Empty:pass
    configs = Empty()
    configs.M5      = path.join(dirs.dump, sname + "2cm5") # we don't do Gem5 simulation for cpu with more than 2 cores
    configs.m5stat  = path.join(configs.M5, "stats.txt")
    configs.m5conf  = path.join(configs.M5, "config.json")
    configs.templ   = path.join(dirs.templates, "mcpat-ruby_22nm_v13_steady.xml")
    configs.XML     = path.join(dirs.dump, sname + "2cxml")
    configs.op      = path.join(dirs.dump, sname + "2c.op")
    configs.pt2c    = path.join(dirs.dump, sname + "2c.ptrace")
    configs.pt      = path.join(dirs.dump, name + ".ptrace")
    configs.gridIR  = path.join(dirs.dump, name + ".gridIR")
    configs.vtrace  = path.join(dirs.dump, name + ".vtrace")
    configs.powerG  = path.join(dirs.dump, name + ".powerG")
    configs.rawpG   = configs.gridIR + "powerG"
    configs.current = path.join(dirs.dump, name + ".current")
    configs.vStep   = path.join(dirs.dump, name + ".vStep")
    configs.iStep   = path.join(dirs.dump, name + ".iStep")
    configs.b       = path.join(dirs.dump, name + ".B")
    configs.v11     = path.join(dirs.dump, name + ".v11")
    configs.flp     = path.join(dirs.config, "Penryn22_ruby_ya_" + n + "c_v13.flp")
    configs.pdn     = path.join(dirs.config, "pdnYi.config")
    return configs

if __name__ == "__main__":
    main()

    
