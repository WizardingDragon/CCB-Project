import multiprocessing
import os
import platform
import re
import subprocess
import sys
import glob
import shutil
import numpy as np

def change_input(filename, frac, seed=None, time=50000):
    """Creates a new dmpci.ms_sim with updated number fraction values (cf dpd doc)"""

    # Fraction of all lipids in the simulation volume
    frac_LT = 0.019994

    # Fraction of lipids in the simulation
    frac_sl = round(1.5/(32**3 *3), 7)
    frac_Lp = round(frac * frac_LT - frac_sl, 7)
    frac_w = round(1 - frac_sl - frac_Lp, 7)

    params = {'Box': "32 32 32\t1 1 1", 'RNGSeed': seed if seed is not None else -521573, 'Step': 0.005, 'Time': time, 
              'SamplePeriod': time //2000, 'AnalysisPeriod': time //20, 'DensityPeriod': time, 'DisplayPeriod': time //20, 'RestartPeriod': time // 2,
              }

    with open(filename, 'rt') as rf:
        with open(filename+'_sim', 'wt') as wf:
            for line in rf:
                if line.startswith('Polymer Water'):
                    line = line.strip().split()
                    line[2] = f"{frac_w:.7f}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')  
                    line = next(rf) 

                if line.startswith('Polymer Lipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_Lp:.7f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    line = next(rf)

                if line.startswith('Polymer	SingleLipid'):
                    line = line.strip().split()
                    line[2] = f"{frac_sl:.7f}"

                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t'.join(line) + '\n')
                    line = next(rf)
                    
                if line.startswith('	Times	0 20000'):
                    line = line.strip().split()
                    line[2] = f"{time}"
                    
                    # Converts list to list[str]
                    line = list(map(str, line))
                    wf.write('\t' + '\t'.join(line) + '\n')  
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

    files = ['dmpci.lp6_eq', 'dpd-linux']
    for file in files:
        shutil.copy(file, folder+file)

    change_input(f'{folder}dmpci.lp6_eq', params['frac'], params['seed'])

    # Starts simulation and deletes the dpd linux file to reduce size when scp-ing folders between computers
    os.system(f'cd {folder} && ./dpd-linux lp6_eq_sim && rm dpd-linux')


def main():
    # Fraction of lipid in the simulation volume andround them to 3 decimals with numpy.around()
    frac = np.around(np.linspace(1.1382353,1.1382353,1), decimals=3)
    
    # Change FOLDER NAME BEFORE ADDING OTHER SEEDS!!!!!!!!!!!!
    np.random.seed(279)
    seeds = np.random.randint(-9999, -1000, size=7)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sims = [{'folder': f'lp6_{seeds[j]}_{frac[i]:.3f}/', 'frac': frac[i], 'seed': seeds[j]} 
            for i in range(len(frac)) for j in range(len(seeds))]
    
    print(sims)
    with multiprocessing.Pool(processes = 7) as p:
        p.map(run_sim, sims)    

    print('Done')


if __name__ == "__main__":
    main()
