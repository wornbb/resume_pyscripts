#!/usr/bin/python
import argparse
import pandas as pd
def mulptrace(i, o ,n):
    class Empty:pass
    args = Empty()
    args.i = i
    args.o = o
    args.n = n
   # read ptrace
    # read it in pieces because it's too big
    chunk = 5000
    dfIter = pd.read_table(args.inputf, chunksize=chunk)
    disposable = False
    with open(args.outputf, 'w') as f:
        for df in dfIter:
            if not disposable:
                headers = list(df)
                headers_size = len(headers)
                # get how many cores simulated
                simulated_num = []
                num = 0
                for component in headers:
                    if component[:-1] == 'FPU':
                        num = num + 1
                simulated_cores = num 
                repeat = int(int(args.ncore) / simulated_cores)
                print("simulated_cores: ",  simulated_cores)
                print("ncore: ", args.ncore)
                print("repeat: ", repeat)
                if repeat % 2 != 0:
                    if repeat != 1:
                        print(repeat)
                        raise RuntimeError('core number is not right')
            if simulated_cores == args.ncore: # this case is only for 2 core CPU. Fix lazy core issue. No longer used.
                print("You are duplicating 2core ptrace to 2core. This feature proves to be very bad. \n Make sure you know what you are doing")
                if not disposable:
                    print('mode fix lazy')
                    # Assumes lazy core alwasy produce 0 power
                    # lets find the components of lazy core
                    for idx in range(chunk):# If it is lazy, we can for sure to find it in the first 10000000000 cycles.    
                        test = df.iloc[idx,:]
                        key = (test==0)
                        if key.any():
                            break
                    # caught 
                    headers = df.columns.values
                    lazy = headers[key]
                    work = headers[~key]
                    # sanity check
                    if key.mean() >= 0.5:
                        print('Those are lazy components: ', lazy)
                        print('Those are work components: ', work)
                        #raise RuntimeError('Big problem, lazier than expected')
                        print('Big problem, lazier than expected')
                    # cp work stats to lazy
                numTag = ['2', '1']
                for lazyComp in lazy:
                    lazyTag = lazyComp[-1]
                    if numTag[0] == lazyTag:
                        workTag = numTag[1]
                    else:
                        workTag = numTag[0]
                    workComp = lazyComp[:-1] + workTag
                    # sanity check
                    if workComp not in work:
                        print('lazy comp: ', lazyComp)
                        print('work comp: ', workComp)
                        print('Big problem, this lazy comp is unique')
                    else:
                        df.loc[:, lazyComp] = df.loc[:, workComp]
            elif simulated_cores > 1: # just duplicate 
                headers = list(df)
                headers_copy = list(headers)
                headers_size = len(headers)
                df = pd.concat([df] * repeat, axis=1)
                new_headers = []
                # duplicate each component 
                # the main job here is to figure out the proper names for new components
                for component in headers:
                    oldTag = int(component[-1])
                    tag = oldTag
                    new_headers.append(component)
                    valid = False
                    while not valid:
                        tag = tag + 1
                        newComp = component[:-1] + str(tag)
                        if newComp not in headers:
                            if newComp not in new_headers:
                                new_headers.append(newComp)
                        if int(tag) == oldTag * repeat:
                            break

                df.columns = new_headers
            else: #In this case, we are duplicating 1 core into multi cores
                pass
            if not disposable:
                df.to_csv(f, index=None, sep='\t', mode='a')
                disposable = True
            else:
                df.to_csv(f, index=None, header=None, sep='\t', mode='a')
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputf', action='store')
    parser.add_argument('-o', dest='outputf', action='store')
    parser.add_argument('-n', dest='ncore', action='store', type=int)
    args = parser.parse_args()
    mulptrace(args.i, args.o, args.n)
