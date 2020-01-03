import os
import re
import sys
import glob

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as integrate
from mpl_toolkits.mplot3d import Axes3D


def parse_analysis_state(folder):
    """Stores all the values of the analysis state in a python dictionary"""

    def get_value_of_key(file_gen):
        """Gets all the numerical values following a key line"""
        value = ""
        line = next(file_gen)

        while re.search(r'^[0-9]', line.strip()) is not None:
            value += '\n'+line.strip()
            line = next(file_gen)
        
        return value


    file = list(filter(lambda x: x.startswith('dmpcas'), os.listdir(folder)))

    if len(file) < 1:
        raise FileNotFoundError (f"dmpcas file not found in {folder}")
    
    discard_keys = ['']
    file = file[0]
    analysis_state = {}

    with open(os.path.join(folder, file), 'rt') as f:
        for line in f: 

            if re.search(r'^[A-Za-z]', line.strip()) is not None:
                if line.startswith('Time'):
                    current_time = line.strip().split()[-1]
                    analysis_state[current_time] = {}

                elif line.strip() in discard_keys:
                    continue

                else:
                    analysis_state[current_time][line.strip()] = get_value_of_key(f)
    
    return analysis_state


def get_displacement(folder):

    displacement = []
    dmpctads_file = glob.glob(f"{folder}dmpctads.*")[0]

    with open(dmpctads_file, 'rt') as f:
        for line in f:
            if re.search(r'^[0-9-]', line) is None:
                continue
            
            displacement.append(list(map(float, line.strip().split())))

    return np.array(displacement)
    

def get_bilayer_data(folder):
    """"""

    bilayer = []
    dmpcaa_file = glob.glob(f"{folder}dmpcaa.*")[0]

    with open(dmpcaa_file, 'rt') as f:
        for line in f:
            if re.search(r'^[0-9-]', line) is None:
                continue
            
            bilayer.append(list(map(float, line.strip().split())))

    return np.array(bilayer)


def get_history_state(folder):
    """"""

    history_state = []
    dmpchs_file = glob.glob(f"{folder}dmpchs.*")[0]

    with open(dmpchs_file, 'rt') as f:

        for line in f:            
            history_state.append(list(map(float, line.strip().split())))

    return np.array(history_state)


def denoising(array, time=None, time_range=(1, 50000)):
    """"""

    diff = array[1:] -array[:-1]
    std = diff[np.abs(diff) > 0.1].std()
    diff[np.abs(diff) > 0.1] = 0
    
    if time is None:
        diff = integrate.cumtrapz(diff, np.linspace(time_range[0], time_range[1]-1, diff.shape[0]), initial=0.0) +array[0]

    else:
        diff = integrate.cumtrapz(diff, time[:-1], initial=0.0) +array[0]

    return diff


def compute_work(x, y, z, t, force=15.0, force_range=(1000, 2000), membrane_thickness=4, polymer_length=3.0):
    """""" 
    
    start_id, stop_id = np.where(t == force_range[0])[0][0], np.where(t == force_range[1])[0][0]
    z = denoising(z, t)

    diff = z[1:] -z[:-1]
    force = np.full(diff[start_id:stop_id].shape, force)
    
    instant_work = force *diff[start_id:stop_id]
    work = integrate.cumtrapz(instant_work, z[start_id:stop_id], initial=0.0)
    # t_in = t[:-1][(t[:-1] >= force_range[0]) & (t[:-1] <= force_range[1]) & (z < (16 + membrane_width /2 +polymer_length /2))]
    t_in = t[:-1][(t[:-1] >= force_range[0]) & (t[:-1] <= force_range[1]) & (z < (16 + membrane_thickness /2 + polymer_length /2))]

    plt.figure()
    plt.plot(t[start_id:stop_id], instant_work)
    if t_in.shape[0] >=1000:
        return
    plt.plot(t_in, work[:t_in.shape[0]])
    plt.xlabel('Time')
    plt.ylabel('Work on Lipid')

    return instant_work, t[start_id:stop_id], work, t_in


def plot_2D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=4):
    """"""
    
    fig = plt.figure()

    # Plots trajectories
    # plt.plot(t, (x), label='X', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0])
    # plt.plot(t, (y), label='Y', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1])
    # plt.plot(t, (z), label='Z', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][2])

    plt.plot(t[:-1], denoising(x, t), label='denois_X', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0])
    plt.plot(t[:-1], denoising(y, t), label='denois_Y', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1])
    plt.plot(t[:-1], denoising(z, t), label='denois_Z', color=plt.rcParams['axes.prop_cycle'].by_key()['color'][2])

    plt.plot([force_range[0], force_range[0]], [0, 32],
             color=plt.rcParams['axes.prop_cycle'].by_key()['color'][3])
    plt.plot([force_range[1], force_range[1]], [0, 32],
             color=plt.rcParams['axes.prop_cycle'].by_key()['color'][3], label="Force Application Range")

    plt.plot([t[1], t[-1]], [0, 0], color=plt.rcParams['axes.prop_cycle'].by_key()['color'][4])
    plt.plot([t[1], t[-1]], [32, 32], color=plt.rcParams['axes.prop_cycle'].by_key()['color'][4], label="Box Boundaries")

    plt.plot([t[1], t[-1]], [16 -membrane_thickness /2, 16 -membrane_thickness /2], 
             color=plt.rcParams['axes.prop_cycle'].by_key()['color'][5])
    plt.plot([t[1], t[-1]], [16 +membrane_thickness /2, 16 +membrane_thickness /2], 
             color=plt.rcParams['axes.prop_cycle'].by_key()['color'][5], label="Membrane expected boundaries (Z axis)")

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Position')


def plot_3D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=4):
    """"""

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plots the trajectory while the Force is applied
    ax.plot(xs=denoising(x, t)[(t[:-1] > force_range[0]) & (t[:-1] < force_range[1])],
            ys=denoising(y, t)[(t[:-1] > force_range[0]) & (t[:-1] < force_range[1])],
            zs=denoising(z, t)[(t[:-1] > force_range[0]) & (t[:-1] < force_range[1])],
            color=plt.rcParams['axes.prop_cycle'].by_key()['color'][3],
            label='Force application period')

    # Plots the rest of the trajectory
    ax.plot(xs=denoising(x, t)[(t[:-1] < force_range[0])],
            ys=denoising(y, t)[(t[:-1] < force_range[0])],
            zs=denoising(z, t)[(t[:-1] < force_range[0])],
            color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0])

    ax.plot(xs=denoising(x, t)[(t[:-1] > force_range[1])],
            ys=denoising(y, t)[(t[:-1] > force_range[1])],
            zs=denoising(z, t)[(t[:-1] > force_range[1])],
            color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0])

    # Plots expected membrane boundaries
    xs, ys = np.meshgrid(np.linspace(0, 32, 33), np.linspace(0, 32, 33))
    ax.plot_wireframe(xs, ys, np.full((33, 33), 16 + (membrane_thickness / 2)),
                      color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], alpha=0.4)
    ax.plot_wireframe(xs, ys, np.full((33, 33), 16 -(membrane_thickness /2)), 
                      color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], alpha=0.4)

    plt.axis([0, 32, 0, 32])
    ax.set_zlim([0, 32])
    plt.legend()


def main():

    # analysis_state = parse_analysis_state('test/')
    # history_state = get_history_state('rs_lp4_-2460_1.0000000/')
    
    # disp = get_displacement('rs_lp4_-2460_1.0000000/')
    # x, y, z, t = disp[:, 1], disp[:, 2], disp[:, 3], disp[:, 0]

    # bilayer = get_bilayer_data('rs_lp4_-2460_1.0000000/')
    # plt.figure()

    # beads = ['H', 'T', 'W', 'HS']
    # for col in range(len(beads)):
    #     plt.plot(history_state[:,0], history_state[:,col+6], label=f"Bead diffusion constant {beads[col]}")

    # polymers = ['Mebrane Lipid', 'Single Lipid']
    # for col in range(len(polymers)):
    # plt.legend()
    
    works4, works6 = [], []
    # for folder in os.listdir('Results/lipid4_fin/'):
    #     file = glob.glob(f"Results/lipid4_fin/{folder}/dmpci.*_rs")

    #     history_state = get_history_state(f"Results/lipid4_fin/{folder}/")
    #     disp = get_displacement(f"Results/lipid4_fin/{folder}/")
    #     x, y, z, t = disp[:, 1], disp[:, 2], disp[:, 3], disp[:, 0]

    #     bilayer = get_bilayer_data(f"Results/lipid4_fin/{folder}/")
    
    
    #     # plot_3D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=5)
    #     # plot_2D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=5)

    #     Fdx, t, W, t_in = compute_work(x, y, z, t, force=50.0, force_range=(1000, 2000), membrane_thickness=5, polymer_length=3)
    #     works4.append(W[t_in.shape[0]])


    for folder in os.listdir('Results/lipid8_2/'):
            file = glob.glob(f"Results/lipid8_2/{folder}/dmpci.*_rs")

            history_state = get_history_state(f"Results/lipid8_2/{folder}/")
            disp = get_displacement(f"Results/lipid8_2/{folder}/")
            x, y, z, t = disp[:, 1], disp[:, 2], disp[:, 3], disp[:, 0]

            bilayer = get_bilayer_data(f"Results/lipid8_2/{folder}/")
        
        
            # plot_3D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=7)
            plot_2D_trajectory(x, y, z, t, force_range=(1000, 2000), membrane_thickness=7)

            Fdx, t, W, t_in = compute_work(x, y, z, t, force=60.0, force_range=(1000, 2000), membrane_thickness=7, polymer_length=4)
            works6.append(W[t_in.shape[0]])

    plt.figure()
    plt.scatter([4] *len(works4), works4)
    plt.scatter([6] *len(works6), works6)
    plt.xlim([3, 11])
    plt.ylim([0, None])

    plt.show()


if __name__ == '__main__':
    main()
