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


def clean_cwd(*args):
    """Removes most of the simulation files from the current directory"""

    # Generator of the files generated for each runs
    mv_files = (file for file in os.listdir() if file.endswith('.vtk')
                or file.endswith('.dat')
                or file.startswith('eeldata')
                or file.startswith('dmpcis.')
                or file.startswith('dmpcls.')
                or file.startswith('dmpchs.')
                or file.startswith('dmpcas.')
                or file.endswith('_sim'))

    # If no argument were given to name the folder, we will default to date and time to name the folder and archive the simulation files.
    folder_loc = '_'.join(list(map(str, args))) if args is not None else time.strftime("%Y.%m.%d-%H%M%S")
    os.makedirs(folder_loc, exist_ok=True)

    for file in mv_files:
        try:
            shutil.move(file, os.path.join(folder_loc, file))
        except:
            print(f"Failed to move {file}")
            raise
        
    print('')


def archive_results(seeds):
    """ Moves all the resulting folders in a single one, in the 'results' folder, by name. """

    # Moves all created folder and result files in a single folder
    datetime = time.strftime("%Y.%m.%d-%H%M%S")
    try:
        os.makedirs(f"Results/{datetime}")
    except:
        print("Failed to create folder Results/{:s}".format(datetime))
        raise

    try:
        shutil.move('results.log', f"Results/{datetime:s}/results.log")        
    except:
        print("Failed to move results.log")

    for seed in seeds:
        mv_folders = (folder for folder in os.listdir() if folder.endswith(str(seed)))
        for folder in mv_folders:
            try:
                shutil.move(folder, f"Results/{datetime}/{folder}")
            except:
                print(f"Failed to move {folder}")
                raise


def change_input(filename, frac, seed=None, time=30000):
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
                    
                if line.strip().split() and line.strip().split()[0] in params.keys():
                    key = line.strip().split()[0]
                    wf.write(f"{key:<12}\t{str(params[key])}\n")

                else:
                    wf.write(line)
                    

def get_lengths(filename, polymer, time, means, stds):
    """Parses 'as' file to get the EE length mean and std, time allows to return the correct ee lengths based on dmpci analysis time"""

    time_toggle = False
    with open(filename, 'rt') as f:
        for line in f:
            if line.startswith(f"Time = {time}"):
                time_toggle = True

            if line.startswith(f"{polymer} EE distance") and time_toggle:
                line = next(f)
                means.append(float(line.strip().split()[0]))
                stds.append(float(line.strip().split()[1]))
                break

        else:
            raise EOFError(f"No {polymer} EE distance found")
        

def get_length_time_serie(file_ext):
    """"""

    n_polymers = get_n_polymers('.ms_sim')
    times, lenghts = [], []
    with open(f'dmpcas{file_ext}', 'rt') as f:
        for line in f:

            if line.startswith("Time"):
                times.append(int(line.strip().split()[-1]))

            if line.startswith("PEG EE distance"):
                line = next(f)
                lenghts.append(float(line.strip().split()[0]))

    time_str = time.strftime("%H%M%S")

    plt.figure(figsize=(10,10))
    plt.plot(times, lenghts)
    plt.ylim(0, None)
    plt.xlabel('Time [ns]')
    plt.ylabel('Mean Polymer EE length')
    plt.savefig(f"{time_str:s}_{n_polymers:d}.png")

    with open('log.log', 'at') as f:
        defalut_out = sys.stdout
        sys.stdout = f

        print(n_polymers)
        print(times)
        print(lenghts)

        sys.stdout = defalut_out


def get_n_polymers(file_ext):

    with open(f"dmpcis{file_ext}", 'rt') as f:
        for line in f:
            if line.startswith("  # of type 1"):
                return int(line.strip().split()[-1])

        else:
            raise EOFError(f"Could not find number of polymers in 'dmpcis{file_ext}'")


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

    sims = [{'folder': f'{frac_Lp[i]:.0f}_{seeds[j]}/', 'frac_p': frac_Lp[i] /(density * V_sim), 'seed': seeds[j]} 
            for i in range(frac_Lp.shape[0]) for j in range(seeds.shape[0])]

    print(sims)

    with multiprocessing.Pool() as p:
        p.map(run_sim, sims)    

    print('Done')


if __name__ == "__main__":
    main()
