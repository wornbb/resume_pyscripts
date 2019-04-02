import directories as dirs
import os.path as path
gem5 = path.join(dirs.gem5, "build/X86_MOESI_hammer-modified/gem5.opt")
gem2mcpat = path.join(dirs.interface, "GEM5ToMcPAT.py")
mcpat = path.join(dirs.mcpat, "mcpat")
mcpat2voltspot = path.join(dirs.interface, "McPATToHotSpot.py")
voltspot = path.join(dirs.voltspot, "voltspot")
