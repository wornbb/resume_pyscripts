import argparse
import numpy as np
import time
def getV11(gridIR, outName):
    with open(outName, 'w') as o,  open(gridIR, 'r') as v :
        notComplete = True
        counter = 0
        # this is a very bad while loop.
        # the intention was to read the input file even if the file is not completed yet.
        # it seem to have much better solutions for the original purpose. 
        # I am too bothered to improve it because this script has very little significance. 
        while notComplete:
            vline = v.readline()
            vmatrix = np.fromstring(vline, sep='    ', dtype='float')
            if vmatrix.size != 0:
                counter = 0
                try:
                    o.write(str(vmatrix[0]) + '\n')
                except:
                    print(vmatrix.size)
                    print(vline)
            else:
                if counter > 5:
                    notComplete = False
                else:
                    counter = counter  + 1
                    time.sleep(60)
                

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate current based on power/voltage, I dont like this way since it should be AC')
    parser.add_argument('-v', action='store', dest='v', help='file path to volts grid')
    parser.add_argument('-o', action='store', dest='o', help='file path to output    ', default='v11')
    args = parser.parse_args()
    getV11(args.v, args.o)

