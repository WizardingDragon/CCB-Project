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


def change_input(filename, frac_Lp, seed=None, time=30000):
    """Creates a new dmpci.ms_sim with updated number fraction values (cf dpd doc)"""

    # Fraction of all lipids in the simulation volume
    frac_LT = 0.02

    # Fraction of octolipids in the simulation
    frac_Lp = round(frac * frac_LT, 5) if frac_Lp > 8e-5 else 0.0
    # Fraction of regular lipids in the simulation volume
    frac_L = frac_LT - frac_Lp
    frac_w = 1 -frac_L -frac_Lp 

    params = {'Box': "64 32 32\t1 1 1", 'RNGSeed': seed if seed is not None else -4073, 'Step': 0.02, 'Time': time, 
              'SamplePeriod': time //1000, 'AnalysisPeriod': time //200, 'DensityPeriod': time, 'DisplayPeriod': time //10, 'RestartPeriod': time,
              }

    with open(filename, 'rt') as rf:
        with open(filename+'_sim', 'wt') as wf:

            for line in rf:

                if line.startswith('Polymer Water'):
                    line = line.strip().split()
                    line[2] = f"{frac_w:.5f}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')  
                    line = next(rf) 

                if line.startswith('Polymer Lipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_L:.5f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    line = next(rf)
                
                if line.startswith('Polymer OctoLipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_Lp:.5f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    line = next(rf)
                    
                if line.startswith('	Times	0 1000'):
                    line = line.strip().split()
                    line[2] = f"{time}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')  
                    line = next(rf) 
                    
                if line.strip().split() and line.strip().split()[0] in params.keys():
                    key = line.strip().split()[0]
                    wf.write(f"{key:<12}\t{str(params[key])}\n")

                else:
                    wf.write(line)
  

def run_sim(params):

    folder = params['folder']

    if os.path.exists(folder):
        shutil.rmtree(folder)

    os.mkdir(folder)

    files = ['dmpci.ms', 'dpd-w10.exe', 'dpd-linux']
    for file in files:
        shutil.copy(file, folder+file)

    change_input(f'{folder}dmpci.ms', params['frac_p'], params['seed'])

    # Starts simulation
    if platform.system().lower() == 'windows':
        os.system(f'cd {folder} && dpd-w10.exe ms_sim')
    else:
        os.system(f'cd {folder} && ./dpd-linux ms_sim')


def main():

    # density, defined in dmpci
    density = 3
    # Water beads volume !! Does not change !!
    V_w = 4 * 0.5 **3
    # Simulation box volume !! Can be changed in dmpci !!
    V_sim = 20 **3
    # Fraction of octolipid in the simulation volume
    frac_Lp = np.array([0.0625, 0.125, 0.25, 0.375])
    
    np.random.seed(279)
    seeds = np.random.randint(-9999, -1000, size=5)

    sims = [{'folder': f'{frac_Lp[i]:.5f}_{seeds[j]}/', 'frac_p': frac_Lp[i] /(density * V_sim), 'seed': seeds[j]} 
            for i in range(frac_Lp.shape[0]) for j in range(seeds.shape[0])]

    print(sims)

    with multiprocessing.Pool() as p:
        p.map(run_sim, sims)    

    print('Done')


if __name__ == "__main__":
    main()
