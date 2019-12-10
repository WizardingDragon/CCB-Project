import os
import re
import sys

import numpy as np 
import matplotlib.pyplot as plt 


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


def main():
    analysis_state = parse_analysis_state('test/')
    print(analysis_state['1000']['Water Density Profile'])


if __name__ == '__main__':
    main()