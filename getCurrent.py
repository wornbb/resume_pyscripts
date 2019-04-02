import argparse
import numpy as np
def getCurrent(powerG, gridIR, outName, step_percycle=5):
    # Remove exsisting file for preparing writing
    # The following commented code by "###" is for only processing desired amount of cycles.
###    cycle = 80000
###    granularity = 5
###    threshold = cycle * granularity
    with open(outName, 'w') as o, open(powerG, 'r') as p, open(gridIR, 'r') as v :
        counter = 0
        # for each line in v, there are 5 (granularity) power 
        for vline in v:
            vmatrix = np.fromstring(vline, sep='    ', dtype='float')
            length = vmatrix.shape[0]
            pmatrix = np.empty([step_percycle, length])
            for idx in range(step_percycle):
                pvec = np.fromstring(p.readline(), sep='    ', dtype='float')
                pmatrix[idx, :] = pvec
            # current = power / voltage
            omatrix = np.divide(pmatrix, vmatrix)
            np.savetxt(o, omatrix, delimiter='   ', fmt='%.6f')
###            counter = counter + 1
###            if counter >= threshold:
###                break
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate current based on power/voltage, I dont like this way since it should be AC')
    parser.add_argument('-p', action='store', dest='p', help='file path to power grid')
    parser.add_argument('-v', action='store', dest='v', help='file path to volts grid')
    parser.add_argument('-o', action='store', dest='o', help='file path to output    ')
    parser.add_argument('-r', action='store', dest='r', help='number of repeats, default 5', default=5, type=int)
    args = parser.parse_args()
    getCurrent(args.p, args.v, args.o, args.r)
