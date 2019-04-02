import os.path as path
home = "/data/yi/voltVio/"
save = "/data/ToMarco"
# anlaysis scripts directories 
anlaysis = path.join(home, "analysis")
mscripts = path.join(anlaysis, "mscripts")
pyscripts = path.join(anlaysis, "pyscripts")
raw = path.join(anlaysis, "raw")
dump = raw
# simualtion related softwares & configurations
simulation = path.join(home, "simulation")
    #softwares
autorun = path.join(simulation, "autorun")
interface = path.join(simulation, "interface")
utils = path.join(simulation, "utils")
softwares = path.join(simulation, "softwares")
gem5 = path.join(softwares, "gem5-stable")
voltspot = path.join(softwares, "voltspot20")
mcpat = path.join(softwares, "mcpat-riscv-old")
    # configurations
description = path.join(simulation, "simDescription")
rcS = path.join(simulation, "rcS")
templates = path.join(simulation, "templates")
config = "/data/yi/voltVio/simulation/simDescription/vp/chips/22nm"