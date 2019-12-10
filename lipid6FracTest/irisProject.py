import multiprocessing
import os
import platform
import re
import subprocess
import sys


def run_sim(params):
    folder = params['folder']

    # Starts simulation
    if platform.system().lower() == 'windows':
        os.system(f'cd {folder} && dpd-w10.exe lp6_eq')
    else:
        os.system(f'cd {folder} && ./dpd-linux lp6_eq')


def main():    
    sims = [{'folder': f'lipid6_0.6'},
            {'folder': f'lipid6_0.66'},
            {'folder': f'lipid6_0.75'},
            {'folder': f'lipid6_0.8'},
            {'folder': f'lipid6_0.9'},
            {'folder': f'lipid6_1.1'},
            {'folder': f'lipid6_1.25'}]

    with multiprocessing.Pool() as p:
        p.map(run_sim, sims)    

    print('Done')


if __name__ == "__main__":
    main()
