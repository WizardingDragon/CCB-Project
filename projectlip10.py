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


def change_input(filename, frac_l=0.019994, force=25.0, time=200_000, seed=None):
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

                elif line.startswith('Command\tConstantForceOnTarget') or line.startswith('Command ConstantForceOnTarget'):
                    line = line.strip().split()

                    if line[3] == "singleLipidHead":
                        line[-1] = f"{force /3:.6f}"  

                    elif line[3] == "lowerHeads":
                        line[-1] = f"{force /3 /(1636):.6f}"

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
        time.sleep(1)

    os.mkdir(folder)

    files = ['dmpci.ms', 'dpd-w10.exe'] if platform.system().lower() == 'windows' \
        else ['dmpci.ms', 'dpd-linux']

    for file in files:
        shutil.copy(file, os.path.join(folder, file))

    change_input(os.path.join(folder, files[0]))
    os.remove(os.path.join(folder, files[0]))

    # Starts simulation
    if platform.system().lower() == 'windows':      
        p = subprocess.run(['cd', f'{folder}', '&&', 'dpd-w10.exe', 'ms_sim'], shell=True, stdout=None)

        if p.returncode == 0:
            print("Simulation finished succesfully!") 
            os.remove(os.path.join(folder, 'dpd-w10.exe'))

        else:
            print(f"Simulation failed with error: '{p.stderr}', error code: '{p.returncode}'")
            # if os.path.exists(folder):
            #     shutil.rmtree(folder)
        
    else:
        os.system(f'cd {folder} && ./dpd-linux ms_sim')
        os.remove(os.path.join(folder, 'dpd-linux'))   


def change_input_rs(filename, force=50, restart_time=50_000, seed=None):
    """Creates a new dmpci.ms_sim with updated number fraction values (cf dpd doc)"""

    def get_n_polymers(filename):
        """Gets the number of membrane lipids from the dmpcis file"""
        
        dmpcis_name = re.sub('dmpci', 'dmpcis', filename)

        with open(dmpcis_name, 'rt') as f:
            for line in f:
                if line.startswith('  # of type 1'):
                    n_polymers = int(line.strip().split()[-1])

        return n_polymers


    n_polymers = get_n_polymers(filename)

    commands = {'ToggleBeadDisplay':                f"1\t\tW",
                'SetCurrentStateCamera':            f"1\t\t0.5 -0.5 -0.5\t0.5 0.5 0.5",
                'SetCurrentStateDefaultFormat':     f"1\t\tParaview\n",

                'SelectPolymerTypeInSimBox':        f"1\t\tsingleLipid\tSingleLipid",
                'SelectBeadTypeInSimBox':           f"1\t\tsingleLipidHead\tHS",
                'SelectBeadTypeInSlice':            f"1\t\tlowerLipidHeads\tH\t0 0 1\t0.5 0.5 0.46875\t0.5 0.5 0.03125\n",

                # 'MSDOfPolymerTarget':	            f"{1}\t\tsingleLipid\tlipidDisplacement\t1\t5000",
                # 'CylinderLinearForceOnTarget':      f"{2}\t\tsingleLipid\tf_anchor\t0 0 1\t0.5 0.5 0.53125\t2",
                # 'FreezeBeadsInSlice':               f"1000\t\t0 0 1\t0\t4",
                # 'ConstantForceOnTarget':	        [f"1000\t\tsingleLipidHead\tf_s\t0 0 1\t{force /3:.6f}",
                #                                      f"1000\t\tlowerHeads\tf_l\t0 0 1\t{force /n_polymers /6:.6f}\n"],

                # 'RemoveCommandTargetActivity':      [f"1000\t\tf_anchor", f"2000\t\tf_s", f"2000\t\tf_l"]

                'MSDOfPolymerTarget':	            f"1\t\tsingleLipid\tlipidDisplacement\t1\t5000",
                'FreezeBeadsInSlice':               f"1000\t\t0 0 1\t0\t4",
                'ConstantForceOnTarget':	        [f"1000\t\tsingleLipidHead\tf_s\t0 0 1\t{force /3:.6f}",
                                                     f"1000\t\tlowerHeads\tf_l\t0 0 1\t{force /n_polymers /6:.6f}\n"],

                'RemoveCommandTargetActivity':      [f"2000\t\tf_s", f"2000\t\tf_l"]
                }

    
    run_id = filename.split('.')[-1]

    with open(filename+'_rs', 'wt') as wf:
        with open(filename, 'rt') as rf:

            for line in rf:
                if line.strip().startswith("State"):
                    wf.write(f"State\trestart\nRunId\t{run_id:s}\nStateId\t{restart_time:d}\n\n")

                    while not line.strip().startswith("Bead"):
                        line = next(rf)

                if line.startswith('Time'):
                    wf.write(f"Time\t\t5000\n")
                    continue

                if line.startswith('Step'):
                    wf.write(f"Step\t\t0.02\n")
                    continue

                if line.startswith('DensityPeriod'):
                    wf.write(f"DensityPeriod\t5000\n")
                    continue

                if line.startswith('RestartPeriod'):
                    wf.write(f"RestartPeriod\t5000\n")
                    continue

                if re.match('\t+Times', line):
                    wf.write(f"\tTimes\t{0}\t5000\n")
                    continue

                if line.startswith('Command'):
                    continue
                    
                wf.write(line)

        for command, value in commands.items():
            if isinstance(value, str):
                wf.write(f"Command {command}\t\t{value}\n")

            elif isinstance(value, list):
                for val in value:
                    wf.write(f"Command {command}\t\t{val}\n")

            else:
                print("I have a bad feeling about this")

    return run_id
  

def run_sim_from_restart_state(params):

    folder = params['folder']

    if os.path.exists(folder):
        shutil.rmtree(folder)   
        time.sleep(1)

    os.mkdir(folder)

    files =  [file for file in os.listdir(params['load_folder']) if re.match(r'^dmpc(i|(rs)).+(sim).*', file)]

    for file in files:
        shutil.copy(os.path.join(params['load_folder'], file), os.path.join(folder, file))

        shutil.copy('dpd-w10.exe', os.path.join(folder, 'dpd-w10.exe')) if platform.system().lower() == 'windows' \
            else shutil.copy('dpd-linux', os.path.join(folder, 'dpd-linux'))

    run_id = change_input_rs(os.path.join(folder, files[0]))

    # Starts simulation
    if platform.system().lower() == 'windows':      
        p = subprocess.run(f"cd {folder} && dpd-w10.exe {run_id}_rs".split(), shell=True, stdout=None)
        # p = subprocess.run(['cd', f'{folder}', '&&', 'dpd-w10.exe', f'{run_id}_rs'], shell=True, stdout=None)

        if p.returncode == 0:
            print("Simulation finished succesfully!") 
            os.remove(os.path.join(folder, 'dpd-w10.exe'))

        else:
            print(f"Simulation failed with error: '{p.stderr}', error code: '{p.returncode}'")
            # if os.path.exists(folder):
            #     shutil.rmtree(folder)
        
    else:
        p = subprocess.run(f"cd {folder} && ./dpd-linux {run_id}_rs".split(), stdout=None)
        os.remove(os.path.join(folder, 'dpd-linux')) 


def main():
    
    np.random.seed(279)
    seeds = np.random.randint(-9999, -1000, size=5)

    lipid_rs_path = "data/stabilizeLipid10/"
    lipid_rs_paths = list(map(lambda x: lipid_rs_path +x, os.listdir(lipid_rs_path)))

    rs_sims = [{'load_folder': path, 'folder': 'rs_' + path.split('/')[-1]} for path in lipid_rs_paths] 

    print("Started at: {}".format(time.strftime("%H:%M:%S", time.localtime())))
    # run_sim_from_restart_state(rs_sims[0])
    # print("Done at: {}".format(time.strftime("%H:%M:%S", time.localtime())))

    with multiprocessing.Pool(4) as pool:
        pool.map(run_sim_from_restart_state, rs_sims)    

    print('Done')


if __name__ == "__main__":
    main()
