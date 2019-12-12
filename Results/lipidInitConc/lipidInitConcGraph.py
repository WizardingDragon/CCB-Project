## Create a tmp file containing only the lines containing "Bilayer Surface Tension" and the corresponding values

import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle

labels = []
files = glob.glob('*/dmpcas.*')
tmp_files = []
for i in range(len(files)):
    labels.append(str(files[i].strip().split('.')[1])[2:-3])
    tmp_files.append(str(files[i].split('/')[0] + '/' + str(files[i].split('.')[1]) + '.tmp'))
    if os.path.exists(tmp_files[i]):
        os.system(f'rm { tmp_files[i] }')
    os.system('grep -A 1 "Bilayer Surface Tension" {} > {}'.format(files[i], tmp_files[i]))

labelValue = {}
for i in range(len(files)):
    with open(tmp_files[i], 'rt') as rf:
        localLines = []
        for line in rf:
            line = (line.strip().split())[0]
            localLines.append(line)
        goodLines = []
        for ind in range(1,300,3):
            goodLines.append(float(localLines[ind]))
        labelValue[labels[i]] = goodLines
            
x_axis = list(range(1000, 101000, 1000))

from itertools import cycle
lines = ["-","--","-.",":"]
linecycler = cycle(lines)

for label in labels:
    plt.plot(x_axis[5:-1], labelValue[label][5:-1], next(linecycler))
plt.legend(labels)
plt.grid()
plt.show()
