import multiprocessing
import os
import platform
import re
import shutil
import subprocess
import sys
import time

import matplotlib.pyplot as plt
import numpy as np


def change_input(filename, frac_l=0.019994, seed=None, time=200_000):
    """Creates a new dmpci.ms_sim with updated number fraction values (cf dpd doc)"""

    frac_sl = round(1.5 /(32**3 *3), 6)
    frac_l = round(frac_l -frac_sl, 6)
    frac_w = round(1 -frac_l -frac_sl, 6)
    
    params = {'Box': "32 32 32\t1 1 1", 'RNGSeed': seed if seed is not None else -4073, 'Step': 0.02, 'Time': time, 
              'SamplePeriod': 100, 'AnalysisPeriod': 1000, 'DensityPeriod': time, 'DisplayPeriod': time //10, 'RestartPeriod': time,
              }

    with open(filename, 'rt') as rf:
        with open(filename+'_sim', 'wt') as wf:

            for line in rf:
                
                if line.startswith('Polymer\tWater') or line.startswith('Polymer Water'):
                    line = line.strip().split()
                    line[2] = f"{frac_w:.6f}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')

                elif line.startswith('Polymer\tLipid') or line.startswith('Polymer Lipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_l:.6f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                
                elif line.startswith('Polymer\tSingleLipid') or line.startswith('Polymer SingleLipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_sl:.6f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    
                # if line.startswith('	Times	0 1000'):
                #     line = line.strip().split()
                #     line[2] = f"{time}"
                    
                #     # Converts list to list[str]
                #     line = list(map(str, line))
                #     wf.write('\t'.join(line) + '\n')  
                #     line = next(rf) 
                    
                # if line.strip().split() and line.strip().split()[0] in params.keys():
                #     key = line.strip().split()[0]
                #     wf.write(f"{key:<12}\t{str(params[key])}\n")

                else:
                    wf.write(line)
  

def run_sim(params):

    folder = params['folder']

    if os.path.exists(folder):
        shutil.rmtree(folder)

    os.mkdir(folder)

    files = ['dmpci.ms', 'dpd-w10.exe'] if platform.system().lower() == 'windows' \
        else ['dmpci.ms', 'dpd-linux']

    for file in files:
        shutil.copy(file, os.path.join(folder, file))

    change_input(os.path.join(folder, 'dmpci.ms'))

    # Starts simulation
    if platform.system().lower() == 'windows':      
        p = subprocess.run(['cd', f'{folder}', '&&', 'dpd-w10.exe', 'ms_sim'], shell=True, stdout=None)

        if p.returncode == 0:
            os.remove(os.path.join(folder, 'dpd-w10.exe'))

        else:
            print(f"Simulation failed with error: '{p.stderr}', error code: '{p.returncode}'")
            # if os.path.exists(folder):
            #     shutil.rmtree(folder)
        
    else:
        os.system(f'cd {folder} && ./dpd-linux ms_sim')
        os.remove(os.path.join(folder, 'dpd-linux'))    


def main():
    
    np.random.seed(279)
    seeds = np.random.randint(-9999, -1000, size=5)

    sims = [{'folder': 'test/',
             }
            ]

    run_sim(sims[0])

    # with multiprocessing.Pool(2) as pool:
    #     pool.map(run_sim, sims)    

    # print('Done')


if __name__ == "__main__":
    main()
