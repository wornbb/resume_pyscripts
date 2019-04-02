import argparse
import numpy as np
def getSize(gridIR):
    # Remove exsisting file for preparing writing
    with open(gridIR, 'r') as v:
        vline = v.readline()
        vmatrix = np.fromstring(vline, sep='    ', dtype='float')
        length = vmatrix.shape[0]
        print(np.sqrt(length))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate current based on power/voltage, I dont like this way since it should be AC')
    parser.add_argument('-v', action='store', dest='v', help='file path to volts grid')
    args = parser.parse_args()
    getSize(args.v)

