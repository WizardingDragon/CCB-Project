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


def change_input(filename, frac_Lp, frac_Lp2 = 0, seed=None, time=30000, force=None, single_timepoint=False):
    """Creates a new dmpci.ms_sim with updated number fraction values (cf dpd doc)"""

    frac_w = 1 - frac_Lp - frac_Lp2

    if single_timepoint:
            params = {'Box': "32 32 32\t1 1 1", 'RNGSeed': seed if seed is not None else -4073, 'Step': 0.02, 'Time': 1, 
              'SamplePeriod': 1, 'AnalysisPeriod':1, 'DensityPeriod': 1, 'DisplayPeriod': 1, 'RestartPeriod': 1,
              }
            time = 1
    else:
        params = {'Box': "32 32 32\t1 1 1", 'RNGSeed': seed if seed is not None else -4073, 'Step': 0.02, 'Time': time, 
                'SamplePeriod': time //1000, 'AnalysisPeriod': time //200, 'DensityPeriod': time, 'DisplayPeriod': time //10, 'RestartPeriod': time,
                }

    with open(filename, 'rt') as rf:
        with open(filename+'_sim', 'wt') as wf:

            for line in rf:

                if line.startswith('Polymer	Water'):
                    line = line.strip().split()
                    line[2] = f"{frac_w:.6f}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')  
                    line = next(rf) 

                if line.startswith('Polymer	Lipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_Lp:.6f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    line = next(rf)

                if line.startswith('Polymer	SingleLipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_Lp2:.6f}"

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

    # run simulation with only one timepoint to get the number of polymers
    change_input(f'{folder}dmpci.ms', params['frac_p1'], seed=params['seed'], single_timepoint=True)
    # Starts simulation
    if platform.system().lower() == 'windows':
        os.system(f'cd {folder} && dpd-w10.exe ms_sim')
    else:
        os.system(f'cd {folder} && ./dpd-linux ms_sim')

    polymer_numbers = get_polymer_number(folder + 'dmpcis.ms_sim')
    
    lone_poly_frac = 1.5 * params['frac_p1'] / polymer_numbers[1]

    change_input(f'{folder}dmpci.ms', params['frac_p1']-lone_poly_frac, frac_Lp2=lone_poly_frac, seed=params['seed'], time=20000)

    set_step_force(folder+'dmpci.ms_sim', polymer_numbers[1]-1, force_step=5, steps=20, time=20000)

    # Starts simulation
    if platform.system().lower() == 'windows':
        os.system(f'cd {folder} && dpd-w10.exe ms_sim')
    else:
        os.system(f'cd {folder} && ./dpd-linux ms_sim')
    
    #remove the dpd exe files
    os.remove(os.path.join(folder, files[1]))
    os.remove(os.path.join(folder, files[2]))



def get_polymer_number(filename):
    poly_length = []

    with open(filename) as f:
        for line in f:
            if line.startswith('  # of type'):
                line = line.strip().split()
                poly_length.append(int(line[4]))
    return poly_length


def set_step_force(file, polymer_number, force_step=2, steps=25, start_time=10000, time=20000):
    with open(file, 'a') as file:
        file.write('\nCommand SelectBeadTypeInSimBox \t1 \t pulled  HS\n')

        slice_plane = 12 / (2*32)
        half_width = 6 / (2*32)
        file.write(f'Command SelectBeadTypeInSlice \t{start_time-1} \t half_membrane H   0 0 1 \t0.5 0.5 {slice_plane} \t0.5 0.5 {half_width}\n')
        

        step_time = (time-start_time)//steps
        for i in range(steps):
            file.write(f'\nCommand ConstantForceOnTarget \t{i*step_time+start_time} \tpulled \t\tfp{i} \t0 0 1 \t{force_step/3}\n')
            file.write(f'Command ConstantForceOnTarget \t{i*step_time+start_time} \thalf_membrane \thm{i} \t0 0 1 \t{2*force_step/(3*polymer_number)}\n')





def main():
    start_time = time.time()
    # density, defined in dmpci
    density = 3
    # Water beads volume !! Does not change !!
    V_w = 4 * 0.5 **3
    # Simulation box volume !! Can be changed in dmpci !!
    V_sim = 20 **3
    # Fraction of octolipid in the simulation volume
    frac_Lp = np.array([0.0625, 0.125, 0.25, 0.375])
    
    np.random.seed(279)
    seeds = np.random.randint(-9999, -1000, size=2)

    # sims = [{'folder': f'Results/force_30_{seeds[j]}/', 'frac_p1': 0.019994, 'frac_p2': 0, 'seed': seeds[j]}
    #              for j in range(seeds.shape[0])]

    sim = {'folder': f'Results/{0.019994:.5f}_{seeds[0]}/', 'frac_p1': 0.019994, 'frac_p2': 0, 'seed': seeds[0]}
    print(sim)

    # with multiprocessing.Pool(6) as p:
    #     p.map(run_sim, sims)   

    run_sim(sim)
    runtime = time.time() - start_time
    print(f'Done. Time elapsed: {runtime}')


if __name__ == "__main__":
    main()
